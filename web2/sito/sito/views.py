from django.http import HttpResponse

def hello_world(request):
  html = "<html><body><p>Hello, world!</p></body></html>"
  return HttpResponse(html)