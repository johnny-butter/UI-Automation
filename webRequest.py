import requests
import bs4


def add_quota(studentId, amount=5):
    student_id = str(studentId)
    with requests.session() as session_requests:
        url = 'https://domain.com'
        landing = session_requests.get(url)

        signin_info = bs4.BeautifulSoup(landing.text, 'html.parser')
        authenticity_token = signin_info.find(
            'meta', attrs={"name": "csrf-token"}).get('content')

        sign_in_data = {'authenticity_token': authenticity_token,
                        'email': 'email@email.com',
                        'password': 'password',
                        }

        session_requests.post(url, data=sign_in_data)

        add_quota_data = {'quotas': amount}

        session_requests.post(url, data=add_quota_data)
