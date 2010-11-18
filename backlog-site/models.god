
digraph name {
  fontname = "Helvetica"
  fontsize = 8

  node [
    fontname = "Helvetica"
    fontsize = 8
    shape = "plaintext"
  ]
  edge [
    fontname = "Helvetica"
    fontsize = 8
  ]





  
    projects_models_SiteStats [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >SiteStats</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">user_count</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">project_count</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">story_count</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">date</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">DateField</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  
    projects_models_PointsLog [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >PointsLog</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">date</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">DateField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">points_claimed</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">points_total</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">content_type</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">object_id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">PositiveIntegerField</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  
    projects_models_Project [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >Project<BR/>&lt;<FONT FACE="Helvetica Italic">Group</FONT>&gt;</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Italic">slug</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Italic">SlugField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Italic">name</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Italic">CharField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Italic">creator</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Italic">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Italic">created</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Italic">DateTimeField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Italic">description</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Italic">TextField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">private</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">BooleanField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">member_users</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ManyToManyField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">points_log</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">GenericRelation</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  
    projects_models_Iteration [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >Iteration</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">name</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">CharField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">detail</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">TextField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">start_date</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">DateField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">end_date</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">DateField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">project</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">default_iteration</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">BooleanField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">points_log</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">GenericRelation</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  
    projects_models_Story [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >Story</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">rank</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">summary</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">TextField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">local_id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">detail</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">TextField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">creator</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">created</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">DateTimeField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">modified</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">DateTimeField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">assignee</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">tags</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">TagField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">points</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">CharField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">iteration</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">project</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">status</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">IntegerField</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  
    projects_models_ProjectMember [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >ProjectMember</FONT></TD></TR>

    
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">id</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">AutoField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">project</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">user</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">ForeignKey</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">away</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">BooleanField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">away_message</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">CharField</FONT
        ></TD></TR>
        
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">away_since</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">DateTimeField</FONT
        ></TD></TR>
        
    
    </TABLE>
    >]
  




  
    
  
    
    
    django_contrib_contenttypes_models_ContentType [label=<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
        ><FONT FACE="Helvetica Bold" COLOR="white"
        >ContentType</FONT></TD></TR>
        </TABLE>
        >]
    
    projects_models_PointsLog -> django_contrib_contenttypes_models_ContentType
    [label="content_type"] ;
    
  
    
    
    django_contrib_auth_models_User [label=<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
        ><FONT FACE="Helvetica Bold" COLOR="white"
        >User</FONT></TD></TR>
        </TABLE>
        >]
    
    projects_models_Project -> django_contrib_auth_models_User
    [label="creator"] ;
    
    
    projects_models_Project -> projects_models_PointsLog
    [label="points_log"] [style="dotted"] [arrowhead=normal arrowtail=normal];
    
  
    
    
    projects_models_Iteration -> projects_models_Project
    [label="project"] ;
    
    
    projects_models_Iteration -> projects_models_PointsLog
    [label="points_log"] [style="dotted"] [arrowhead=normal arrowtail=normal];
    
  
    
    
    django_contrib_auth_models_User [label=<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
        ><FONT FACE="Helvetica Bold" COLOR="white"
        >User</FONT></TD></TR>
        </TABLE>
        >]
    
    projects_models_Story -> django_contrib_auth_models_User
    [label="creator"] ;
    
    
    django_contrib_auth_models_User [label=<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
        ><FONT FACE="Helvetica Bold" COLOR="white"
        >User</FONT></TD></TR>
        </TABLE>
        >]
    
    projects_models_Story -> django_contrib_auth_models_User
    [label="assignee"] ;
    
    
    projects_models_Story -> projects_models_Iteration
    [label="iteration"] ;
    
    
    projects_models_Story -> projects_models_Project
    [label="project"] ;
    
  
    
    
    projects_models_ProjectMember -> projects_models_Project
    [label="project"] ;
    
    
    django_contrib_auth_models_User [label=<
        <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
        <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
        ><FONT FACE="Helvetica Bold" COLOR="white"
        >User</FONT></TD></TR>
        </TABLE>
        >]
    
    projects_models_ProjectMember -> django_contrib_auth_models_User
    [label="user"] ;
    
  


}

