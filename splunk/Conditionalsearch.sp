| tstats count where index=* AND searchmatch="string1" by runID
| where count > 0
| fields runID
| map search="search string2 AND runID=$runID$ 
              | eval found=1 
              | table runID found" 
| append 
    [ | stats count 
      | where count=0 
      | eval message=\"No results found for string2 with the runID from string1\" 
      | table message 
    ]
