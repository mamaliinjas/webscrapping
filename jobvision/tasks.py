from celery import shared_task
from .views import get_content
from .models import Job
from bs4 import BeautifulSoup

@shared_task
def scrape_jobs():
    print("Running daily job scrape...")

    html_content = get_content("python-developer")
    soup = BeautifulSoup(html_content, 'html.parser')
    job_items = soup.find_all('job-card', class_='col-12 row cursor px-0 ng-star-inserted')

    Job.objects.all().delete()

    for job in job_items[:10]:  
        title_tag = job.find('div', class_='job-card-title')
        title = title_tag.text.strip() if title_tag else "No Title"

        company_tag = job.find('a', class_='text-black line-height-24')
        company = company_tag.text.strip() if company_tag else "No Company"

        location_tag = job.find('div', class_='text-secondary')
        location = location_tag.text.strip() if location_tag else "No Location"

        Job.objects.create(
            title=title,
            company=company,
            location=location
        )

    print("Job scraping completed!")