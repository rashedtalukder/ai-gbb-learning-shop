import requests

def make_requests(url, num_requests, user_prompt):
    encoded_prompt = requests.utils.quote(user_prompt)
    for i in range(num_requests):
        response = requests.get(url + "&prompt=" + encoded_prompt)
        print(f'{i}-{response.text}\n')

def main():
    url = input("Enter the URL: ")
    num_requests = int(input("Enter the number of requests: "))
    prompt = input("Enter the prompt: ")
    make_requests(url, num_requests, prompt)

if __name__ == "__main__":
    main()