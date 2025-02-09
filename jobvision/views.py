from django.shortcuts import render
from .models import Job
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from django.db.models import Q

def get_content(job):
    job = job.replace(" ", "%20")  
    url = f"https://jobvision.ir/jobs/keyword/{job}/category/in-tehran?page=1&sort=1"

    print(f"Fetching URL: {url}")  

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(5) 

    html_content = driver.page_source
    driver.quit()

    return html_content


def home(request):
    job_info_list = []

    if 'job' in request.GET:
        job = request.GET.get('job')
        html_content = get_content(job)

        if not html_content:
            return render(request, 'jobvision/home.html', {'jobs': job_info_list})

        soup = BeautifulSoup(html_content, 'html.parser')
        job_items = soup.find_all('job-card', class_='col-12 row cursor px-0 ng-star-inserted')

        print(f"Number of job items found: {len(job_items)}") 

        Job.objects.all().delete()

        for job in job_items[:10]:
            title_tag = job.find('div', class_='job-card-title')
            title = title_tag.text.strip() if title_tag else "No Title"

            company_tag = job.find('a', class_='text-black line-height-24')
            company = company_tag.text.strip() if company_tag else "No Company"

            location_tag = job.find('div', class_='text-secondary')
            location = location_tag.text.strip() if location_tag else "No Location"

            print(f"Job Data: Title: {title}, Company: {company}, Location: {location}")

            try:
                Job.objects.create(
                    title=title,
                    company=company,
                    location=location
                )
                print(f"Saved job: {title}")
            except Exception as e:
                print(f"Error saving job: {e}")


    search_query = request.GET.get('search', '')
    if search_query:
        jobs = Job.objects.filter(
            Q(title__icontains=search_query) | Q(company__icontains=search_query)
        )
    else:
        jobs = Job.objects.all()

    return render(request, 'jobvision/home.html', {'jobs': jobs, 'search_query': search_query})