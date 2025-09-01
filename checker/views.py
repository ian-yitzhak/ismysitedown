import requests
import time
from django.shortcuts import render
from django.contrib import messages
from .forms import URLCheckForm
from .models import WebsiteCheck

def check_website_status(url):
    """Check if a website is up or down and get its content"""
    try:
        # Add protocol if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response_time = round((time.time() - start_time) * 1000, 2)  # in milliseconds
        
        status = 'up' if response.status_code == 200 else 'down'
        
        # Get content if status is up
        content = ''
        content_preview = ''
        if status == 'up' and response.content:
            try:
                content = response.text
                # Create a preview (first 200 characters of visible text)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                
                content_preview = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
                
            except Exception:
                content_preview = "Content could not be parsed"
        
        return {
            'status': status,
            'status_code': response.status_code,
            'response_time': response_time,
            'error_message': '',
            'content': content,
            'content_preview': content_preview
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': str(e),
            'content': '',
            'content_preview': ''
        }

def index(request):
    form = URLCheckForm()
    result = None
    recent_checks = WebsiteCheck.objects.all()[:10]
    
    if request.method == 'POST':
        form = URLCheckForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Check website status
            check_result = check_website_status(url)
            
            # Save to database
            website_check = WebsiteCheck.objects.create(
                url=url,
                status=check_result['status'],
                response_time=check_result['response_time'],
                status_code=check_result['status_code'],
                error_message=check_result['error_message'],
                content=check_result['content'],
                content_preview=check_result['content_preview']
            )
            
            result = {
                'url': url,
                'status': check_result['status'],
                'status_code': check_result['status_code'],
                'response_time': check_result['response_time'],
                'error_message': check_result['error_message'],
                'content': check_result['content'],
                'content_preview': check_result['content_preview']
            }
            
            # Add success/error message
            if check_result['status'] == 'up':
                messages.success(request, f"Website {url} is UP!")
            else:
                messages.error(request, f"Website {url} is DOWN!")
    
    return render(request, 'checker/index.html', {
        'form': form,
        'result': result,
        'recent_checks': recent_checks
    })