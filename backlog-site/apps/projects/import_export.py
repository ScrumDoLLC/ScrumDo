from django.http import HttpResponse
import StringIO
from xlrd import open_workbook
import xlwt
from xml.dom.minidom import Document
import csv
import re

from projects.models import Story

import logging

logger = logging.getLogger(__name__)

ezxf = xlwt.easyxf

def exportIteration(iteration, format ):
  """ Exports an iteration, format should be xls, xml or csv. """
  logger.info("Exporting iteration %s %d" % (iteration.project.slug, iteration.id) )
  if format == "xls":
    return _exportExcel( iteration )
  elif format == "xml":
    return _exportXML( iteration )
  else:
    return _exportCSV( iteration )


def importIteration(iteration, file , user):
  m = re.search('\.(\S+)', file.name)

  if m.group(1) == "xml" :
    return _importXMLIteration(iteration, file, user)
  elif m.group(1) == "xls" :
    return _importExcelIteration(iteration, file, user)
  else:
    return _importCSVIteration(iteration, file, user)
    
    
def _getHeaders( project ):
  """Returns an array of tupples with info on columns.
      (target width, title, function to get the data from a story, excel output format, function to assign the value to a story)
  """
  wrap_xf = ezxf('align: wrap on, vert top')
  numeric_xf = ezxf('align: wrap on, vert top, horiz right')
  
  # Some quick methods to define how imported field values are set in a story.
  # This is one place we can do any logic to clean up the data.
  def setId(story,value):
    story.local_id=int(value)
  def setSummary(story,value):
    story.summary=str(value)
  def setDetail(story,value):
    story.detail=str(value)
  def setPoints(story,value):
    try:
      story.points=str(value)
    except:
      story.points = "?"
    if story.points == "":
      story.points = "?"
  def setStatus(story,value):
    try:
      story.status = Story.STATUS_REVERSE[value]
    except:
      pass # Ignore invalid statuses?      
  def setAssignee(story,value):
    pass # TODO!
  def setRank(story,value):
    try:
      story.rank = int(value)
    except:
      story.rank = story.iteration.stories.count()
  def setExtra1(story,value):
    story.extra_1 = str(value)
  def setExtra2(story,value):
    story.extra_2 = str(value)
  def setExtra3(story,value):
    story.extra_3 = str(value)
  
  headers = [ (50,"Story ID", lambda story: story.local_id ,numeric_xf, setId),
             (350,"Summary", lambda story: story.summary,wrap_xf, setSummary),
             (300,"Detail", lambda story: story.detail ,wrap_xf, setDetail),
             (50,"Points", lambda story: int(story.points) if story.points.isdigit() else story.points, numeric_xf, setPoints),
             (70,"Status", lambda story: Story.STATUS_CHOICES[story.status-1][1] ,wrap_xf, setStatus), # TODO the setting function             
             (50,"Rank", lambda story: story.rank,numeric_xf ,  setRank),          
             (200,project.extra_1_label, lambda story: story.extra_1,wrap_xf,  setExtra1), 
             (200,project.extra_2_label, lambda story: story.extra_2,wrap_xf,  setExtra2), 
             (200,project.extra_3_label, lambda story: story.extra_3,wrap_xf,  setExtra3) ]

  if project.use_assignee:  
    headers.insert(6, (70,"Assignee", lambda story:  story.assignee.username if story.assignee is not None else "" ,wrap_xf, setAssignee))
  return headers
          
def _exportExcel( iteration ):
  """ Exports the stories in an iteration as an excel sheet. """
  response = HttpResponse( mimetype="Application/vnd.ms-excel")
  response['Content-Disposition'] = 'attachment; filename=iteration.xls'
  stories = iteration.stories.all().order_by("rank")
  w = xlwt.Workbook()
  ws = w.add_sheet('Iteration Export')
  
  headers = _getHeaders(iteration.project)
  heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')  
  for idx,header in enumerate(headers):
    ws.write(0,idx,header[1],heading_xf)
    ws.col(idx).width = 37*header[0]

  for idx, story in enumerate(stories):
    for hidx, header in enumerate(headers):
      f = header[2]
      ws.write(1+idx,hidx, f(story), header[3] )


  w.save(response)
  return response
  


def _exportXML( iteration ):
  """ Exports the stories in an iteration as XML """  
  stories = iteration.stories.all().order_by("rank")
  doc = Document()  
  iteration_node = doc.createElement("iteration")
  doc.appendChild(iteration_node)

  headers = _getHeaders(iteration.project)  
  
  for idx, story in enumerate(stories):
    row = []
    story_node = doc.createElement("story")
    iteration_node.appendChild( story_node )
    for hidx, header in enumerate(headers):
      f = header[2]
      story_node.setAttribute(_toXMLNodeName(header[1]), str(f(story)).replace("\n"," ").replace("\r",""))
      # TODO: There's a bug in the minidom implementation that doesn't convert newlines to their entities, and there's
      #       no good work-around I can find without monkey patching minidom


  response = HttpResponse(doc.toprettyxml(indent="  "), mimetype="text/xml") 
  response['Content-Disposition'] = 'attachment; filename=iteration.xml'
  return response
  
def _toXMLNodeName( name ):
  return name.replace(" ","_").lower()

def _exportCSV( iteration ):
  """ Exports the stories in an iteration as CSV """
  response =  HttpResponse( mimetype="text/csv") 
  response['Content-Disposition'] = 'attachment; filename=iteration.csv'
  stories = iteration.stories.all().order_by("rank")

  writer = csv.writer(response, delimiter=',' ,  quoting=csv.QUOTE_ALL, escapechar='\\')
    
  headers = _getHeaders(iteration.project)  
  row = []
  for idx,header in enumerate(headers):
    row.append(header[1])
  
  writer.writerow( row )
  
  for idx, story in enumerate(stories):
    row = []
    for hidx, header in enumerate(headers):
      f = header[2]
      row.append( f(story) )
    writer.writerow( row )

  return response



def _importData( data, iteration , user):
  imported = 0
  failed = 0
  for row in data:
    if _importSingleRow(row, iteration, user):
      imported += 1
    else:
      failed += 1
  logger.info("Imported %d records, failed on %d" % (imported,failed))
  return (imported,failed)
      

def _getFieldFromImportData( data, field_name ):
  """ This method returns a value for a given field.  Generally, it's used for translating user data
      into values suitable for a story.  """
  # TODO - Right now, we do only exact matches, we might want a more intelligent
  #        search scheme to accept a wider variety of import formats.
  #        For instance, case insensitive, ignore whitespace, whatever.

  rv = data.get(field_name)
  if( rv == None ):
    rv = data.get( _toXMLNodeName(field_name) )    
  return rv;
  
  
def _importSingleRow( row, iteration, user):
  try:
    local_id = _getFieldFromImportData( row, "Story ID" )
    story = None
    if local_id != None:
      try:
        story = Story.objects.get( project=iteration.project, local_id=int(local_id) )  
        logger.debug("Found story to update (%s)" % local_id)
      except:
        # Story didn't exist already, so we'll be making a new one
        # This is a little dangerous if there was a story id set, since we'll now be ignoreing
        # that and that might not be what the user intended.
        story = Story(project=iteration.project, iteration=iteration, local_id=iteration.project.getNextId() )  
        story.creator = user
        logger.debug("Creating new story to import into.")
  
  
    # I guess a user could move rows from one iteration export to another, so set it here.
    story.iteration = iteration
  
    headers = _getHeaders(iteration.project)
    for header in headers:
      value = _getFieldFromImportData( row, header[1] )
      if value != None:
        try:
          f = header[4]  # This should be a method capable of setting the property
          logger.debug("Setting %s to %s" % (header[1], str(value) ) )        
          f(story, value)
        except:
          logger.debug("Failed to set %s to %s, ignoring." % (header[1], str(value) ) )
  
    story.save()
    return True
  except:
    logger.debug("Failed to import a record.")
    return False


    
def _importExcelIteration(iteration, file, user):
  stories = []
  workbook = open_workbook(file_contents=file.read())
  sheet = workbook.sheets()[0]
  count = 0
  headers = _getHeaders( iteration.project )
  import_data = []
  for row in range(1,sheet.nrows):
    rowData = {}    
    count += 1
    for col in range( sheet.ncols  ):
      header = sheet.cell(0,col).value
      val = sheet.cell(row,col).value
      rowData[header] = val
    import_data.append( rowData )
  logger.info("Found %d rows in an excel sheet " % count)
  _importData( import_data , iteration, user)
    


def _importXMLIteration(iteration, file, user):
  pass

def _importCSVIteration(iteration, file, user):
  pass
  
