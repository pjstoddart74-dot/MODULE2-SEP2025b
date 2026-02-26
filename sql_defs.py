from __future__ import annotations
## Central place for your static SQL statements.
#ASSETS_SQL = ("""
#select * from openquery(SUMAYRISE,'SELECT  UNITID,  UNITNO, LOCATION,STREET, UNITS.STREETID,  INSTALLED,SERVICEOWN FROM Units INNER JOIN STREETS ON UNITS.STREETID =STREETS.STREETID where archived = false AND UNITTYPE = ''G''')
#"""
#).strip()

#ASSETS_SQL = ("""
#select * from openquery(SUMAYRISE,'SELECT   UNITID,  UNITNO, LOCATION,STREET, UNITS.STREETID,  INSTALLED,SERVICEOWN FROM Units INNER JOIN STREETS ON UNITS.STREETID =STREETS.STREETID where archived = false and unittype IN (''Z'',''Y'',''1'')  AND (SERVICEOWN <> ''NE UG'' AND SERVICEOWN <> ''NE OH'') AND UNITS.STREETID <> ''006496''')
#"""
#).strip()

ASSETS_SQL = ("""
select * from openquery(SUMAYRISE,'SELECT   UNITID,  UNITNO, LOCATION,STREET, UNITS.STREETID,  INSTALLED,SERVICEOWN FROM Units INNER JOIN STREETS ON UNITS.STREETID =STREETS.STREETID where archived = false and unittype IN (''C'',''D'',''A'',''L'')  AND (SERVICEOWN <> ''NE UG'' AND SERVICEOWN <> ''NE OH'') AND UNITS.STREETID <> ''006496''')
"""
).strip() ##4516 - 05/01/2026
          ##4484 - 10/02/2026


CABLENOD_SQL = (
    """
   select * from openquery(SUMAYRISE,'SELECT * FROM CABLENOD')
    """
).strip()

ALL_TABLE_SQL = {
    'ASSETS': ASSETS_SQL,
    'CABLENOD': CABLENOD_SQL,
}
