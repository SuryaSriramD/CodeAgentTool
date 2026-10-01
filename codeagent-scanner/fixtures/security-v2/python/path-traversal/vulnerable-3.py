def handler(request):
    name = request.GET["name"]
    return open(f"/srv/{name}").read()
