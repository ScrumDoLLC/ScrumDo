# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA



import StringIO
import csv
import re

from xml.dom.minidom import Document, parse
from django.http import HttpResponse

import xlwt
from xlrd import open_workbook

from projects.models import Story
import logging

logger = logging.getLogger(__name__)

ezxf = xlwt.easyxf

def exportIteration(iteration, format ):
    """ Exports an iteration, format should be xls, xml or csv. """
    logger.info("Exporting iteration %s %d" % (iteration.project.slug, iteration.id) )
    if format.lower() == "xls" :
        return _exportExcel( iteration )
    elif format.lower() == "xml":
        return _exportXML( iteration )
    else:
        return _exportCSV( iteration )


def importIteration(iteration, file , user):
    """ Imports data to an iteration.  Both updating and creating stories is supported.
        file can be either Excel, XML, or CSV """
    m = re.search('\.(\S+)', file.name)

    if m.group(1).lower() == "xml" :
        return _importXMLIteration(iteration, file, user)
    elif m.group(1).lower() == "xls" :
        return _importExcelIteration(iteration, file, user)
    elif m.group(1).lower() == "xlsx" :
        logger.info("Tried to import xlsx file :(")
        user.message_set.create(message="Please save your file as an .xls Excel file before importing.")
        return False
    else:
        # Assume CSV, hope for the best.
        return _importCSVIteration(iteration, file, user)


def exportProject( project ):
    response = HttpResponse( mimetype="Application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename=project.xls'
    stories = project.stories.all().order_by("iteration","rank")
    w = xlwt.Workbook(encoding='utf8')
    ws = w.add_sheet( "All Stories" )
    headers = _getHeaders(project)
    iter_format = ezxf('align: wrap on, vert top')
    headers = [(100,"Iteration", lambda story: story.iteration.name , iter_format , None)] + headers
    
    heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
    date_xf = xlwt.XFStyle()
    date_xf.num_format_str = 'MM/dd/YYYY'
    
    # Write out a header row.
    for idx,header in enumerate(headers):
        ws.write(0,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]
        
    # Write out the first sheet of all the stories
    for idx, story in enumerate(stories):
        for hidx, header in enumerate(headers):
            f = header[2]
            ws.write(1+idx,hidx, f(story), header[3] )   
            
    headers = _getHeaders(project)
    
    # Create the iteration sheet (it gets filled in below the tags sheet)
    iteration_ws = w.add_sheet("Iterations")
    for idx,header in enumerate( [("Iteration",150),("Start",100),("End",100),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60) ] ):
        iteration_ws.write(0,idx,header[0],heading_xf)
        iteration_ws.col(idx).width = 37*header[1]

    # Collect tags
    tags = {}
    for story in stories:
        for tag in story.story_tags.all():
            tagname = tag.name
            if tagname in tags:
                tags[tagname].append( story )
            else:
                tags[tagname] = [story]

    # Write out the tags sheet.
    if len( tags ) > 0:
        ws = w.add_sheet( "Tags" )      
        for idx,header in enumerate( [("Tag",150),("Stories",50),("Stories Claimed",60),("Points",50),("Points Claimed",60)] ):
            ws.write(0,idx,header[0],heading_xf)
            ws.col(idx).width = 37*header[1]          
        for idx,tag in enumerate( tags ):
            stories = tags[tag]
            completed_stories = [story for story in stories if story.status==Story.STATUS_DONE ] 
            ws.write(idx+1,0,tag)
            ws.write(idx+1,1, len(stories) )
            ws.write(idx+1,2, len(completed_stories) )
            ws.write(idx+1,3, reduce( lambda total,story: total+story.points_value(), stories, 0 ) )
            ws.write(idx+1,4, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )

    
    # Write data to the iteration sheet, plus create one sheet per iteration.
    for itIdx, iteration in enumerate(project.iterations.all()):
        iteration_stories = iteration.stories.all()
        completed_stories = [story for story in iteration_stories if story.status==Story.STATUS_DONE ] 
        iteration_ws.write(itIdx+1, 0, iteration.name )
        iteration_ws.write(itIdx+1, 1, iteration.start_date , date_xf)
        iteration_ws.write(itIdx+1, 2, iteration.end_date , date_xf)        
        iteration_ws.write(itIdx+1, 3, len(iteration_stories) )
        iteration_ws.write(itIdx+1, 4, len(completed_stories) )
        iteration_ws.write(itIdx+1, 5, reduce( lambda total,story: total+story.points_value(), iteration_stories, 0 ) )
        iteration_ws.write(itIdx+1, 6, reduce( lambda total,story: total+story.points_value(), completed_stories, 0 ) )        
        ws = w.add_sheet( cleanWorksheetName(iteration.name) )
        
        for idx,header in enumerate(headers):
            ws.write(0,idx,header[1],heading_xf)
            ws.col(idx).width = 37*header[0]
        for idx, story in enumerate(iteration_stories):
            for hidx, header in enumerate(headers):
                f = header[2]
                ws.write(1+idx,hidx, f(story), header[3] )

     
    w.save(response)
    return response


def _getHeaders( project ):
    """Returns an array of tupples with info on columns.
        (target width, title, function to get the data from a story, excel output format, function to assign the value to a story)
    """
    # There's some excel-specific data mixed in here that doesn't entirely fit, but I'm leaving it for now.
    wrap_xf = ezxf('align: wrap on, vert top')
    numeric_xf = ezxf('align: wrap on, vert top, horiz right')

    # Some methods to define how imported field values are set in a story.
    # This is one place we can do any logic to clean up the data.
    def intOrString( value ):
        try:
            if int(value) == float(value):
                return int(float(value))
        except:
            pass
        return value
    def setId(story,value):
        pass
    def setSummary(story,value):
        story.summary=str(value)
    def setDetail(story,value):
        story.detail=str(value)
    def setPoints(story,value):
        try:
            story.points=float(value)
        except:
            if value == "":
                story.points = "?"
            else:
                story.points = value


    def setStatus(story,value):
        try:
            story.status = Story.STATUS_REVERSE[value]
        except:
            pass # Ignore invalid statuses?
    def setAssignee(story,value):
        member = story.project.get_member_by_username(value)
        story.assignee = member

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
    def setTags( story, value ):
        story.tags = str(value)

    headers = [ (50,"Story ID", lambda story: story.local_id ,numeric_xf, setId),
               (350,"Summary", lambda story: story.summary,wrap_xf, setSummary),
               (300,"Detail", lambda story: story.detail ,wrap_xf, setDetail),
               (50,"Points", lambda story: int(story.points) if story.points.isdigit() else story.points, numeric_xf, setPoints),
               (70,"Status", lambda story: Story.STATUS_CHOICES[story.status-1][1] ,wrap_xf, setStatus),
               (50,"Rank", lambda story: story.rank,numeric_xf ,  setRank),
               (80,"Tags", lambda story: story.tags,numeric_xf ,  setTags) ]


    # And some optional columns that depend on project settings:

    if project.use_assignee:
        headers.insert(6, (70,"Assignee", lambda story:  story.assignee.username if story.assignee is not None else "" ,wrap_xf, setAssignee))

    if project.use_extra_1:
        headers.append((200,project.extra_1_label, lambda story: story.extra_1,wrap_xf,  setExtra1))

    if project.use_extra_2:
        headers.append( (200,project.extra_2_label, lambda story: story.extra_2,wrap_xf,  setExtra2) )

    if project.use_extra_3:
        headers.append( (200,project.extra_3_label, lambda story: story.extra_3,wrap_xf,  setExtra3) )

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

    # Write out a header row.
    for idx,header in enumerate(headers):
        logger.debug(header[1])
        ws.write(0,idx,header[1],heading_xf)
        ws.col(idx).width = 37*header[0]

    # Write out all the data.
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
            # TODO (Future Enhancement): There's a bug in the minidom implementation that doesn't convert newlines to their entities inside attributes,
            #      and there's no good work-around I can find without monkey patching minidom itself.
            #      We should generally recommend people stick to excel or CSV files.

    response = HttpResponse(doc.toprettyxml(indent="  "), mimetype="text/xml")
    response['Content-Disposition'] = 'attachment; filename=iteration.xml'
    return response

def _toXMLNodeName( name ):
    return re.sub('[^a-zA-Z0-9_-]',"",name.replace(" ","_").lower())

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
    """ Imports data from a python object to an iteration.
        The idea here is that all the import mechanisms (CSV, XML, XLS) can translate
        their input to a python object hierarchy, and they all can pass that off to
        this method to do the actual import so we only have to write the sync-code
        once.

        data should be an array of python dict like objects, where the keys are
        the names from the getHeaders call, and the values are the user's input.
        """
    imported = 0
    failed = 0
    for row in data:
        if _importSingleRow(row, iteration, user):
            imported += 1
        else:
            failed += 1
    logger.info("Imported %d records, failed on %d" % (imported,failed))
    if failed == 0:
        user.message_set.create(message="Imported %d records." % imported )
    else:
        user.message_set.create(message="Imported %d records, failed on %d" % (imported,failed))
    return (imported,failed)


def _getFieldFromImportData( data, field_name ):
    """ This method returns a value for a given field.  Generally, it's used for translating user data
        into values suitable for a story.  """
    # TODO (Future Enhancement) - Right now, we do only exact matches, we might want a more intelligent
    #        search scheme to accept a wider variety of import formats.
    #        For instance, case insensitive, ignore whitespace, whatever.

    rv = data.get(field_name)
    if( rv == None ):
        # If we didn't find one, lets try an alternative naming...
        rv = data.get( _toXMLNodeName(field_name) )

    return rv;


def _importSingleRow( row, iteration, user):
    try:
        local_id = _getFieldFromImportData( row, "Story ID" )
        story = None
        if local_id != None:
            try:
                story = Story.objects.get( project=iteration.project, local_id=int(local_id) )
                logger.debug("Found story to update (%d)" % int(local_id) )
            except:
                # Story didn't exist already, so we'll be making a new one
                # This is a little dangerous if there was a story id set, since we'll now be ignoring
                # that and that might not be what the user intended.
                story = Story(project=iteration.project, iteration=iteration, local_id=iteration.project.getNextId() )
                story.creator = user
                logger.debug("Creating new story to import into.")


        # A user could move rows from one iteration export to another, so set it here. It'll probably be rare to actually happen.
        story.iteration = iteration

        headers = _getHeaders(iteration.project)
        for header in headers:
            value = _getFieldFromImportData( row, header[1] )
            if value != None:
                try:
                    f = header[4]  # This should be a method capable of setting the property
                    f(story, value)
                    # logger.debug("Setting %s to %s" % (header[1],value) )
                except:
                    logger.info("Failed to set %s to %s, ignoring." % (header[1], str(value) ) )

        story.save()
        return True
    except Exception as e:
        logger.debug("Failed to import a record. %s" % e)
        return False



def _importExcelIteration(iteration, file, user):
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
    xml = parse( file )
    import_data = []
    count = 0
    for story_node in xml.getElementsByTagName("story"):
        attrs = story_node.attributes
        import_row = {}
        for attrName in attrs.keys():
            import_row[attrName] = attrs[attrName].nodeValue
        count += 1
        import_data.append(import_row)
    logger.info("Found %d rows in an XML file" % count)
    _importData( import_data, iteration, user )




def _importCSVIteration(iteration, file, user):
    import_file = csv.reader( file , delimiter=',' ,  quoting=csv.QUOTE_ALL, escapechar='\\' )
    try:
        headers = None
        import_data = []
        count = 0
        for row in import_file:
            try:
                if headers == None:
                    headers = row
                else:
                    import_row = {}
                    for idx,header in enumerate(headers):
                        import_row[header] = row[idx]
                        #logger.debug("Import field %s as %s"%(header, row[idx]) )
                    count += 1
                    import_data.append( import_row )
            except:
                logger.warn("Failed to import CSV row")
    except:
        logger.info("Failed to import CSV file")
    logger.info("Found %d rows in a CSV file" % count)
    _importData( import_data, iteration, user )

def cleanWorksheetName( name ):
    invalidchars = "[]*/\?:=;"    
    tmp = name
    for char in invalidchars:
        tmp = tmp.replace(char,"")
    tmp = tmp[:31]
    return tmp
