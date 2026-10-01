def handler(request, cursor):
    sort = request.GET["sort"]
    cursor.execute("SELECT * FROM users ORDER BY %s" % sort)
