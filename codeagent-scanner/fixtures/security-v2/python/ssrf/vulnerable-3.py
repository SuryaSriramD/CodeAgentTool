import requests
def handler(request):
    url = request.POST.get("endpoint")
    return requests.get(url, timeout=2).status_code
