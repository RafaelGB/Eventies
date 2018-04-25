from django.db import connection

def restart_csv(path):
    with connection.cursor() as cursor:
        cursor.execute("copy (SELECT ev.id,signedup.user_id,ev.views FROM \"public\".\"events_event\" AS ev LEFT JOIN \"public\".\"events_event_signed_up\" AS signedup ON ev.id=signedup.event_id ORDER BY -ev.views) TO '"+path+"' DELIMITER ',' CSV")