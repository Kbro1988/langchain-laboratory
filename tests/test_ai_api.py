from pathlib import Path
import os
from unittest import TestCase, main as unittest_main

import openai

class AI_api_test(TestCase):

    ROOT = Path(os.getcwd())

    def test_openai_api_key(self):
        env_file = self.ROOT.joinpath('.env')
        self.assertTrue(env_file.exists())
        from dotenv import load_dotenv
        load_dotenv(env_file)
        try:
            openai.api_key = os.environ['OPENAI_API_KEY']
        except:
            self.fail(f"OPENAI_API_KEY not found. Check the .env file.")
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                        messages=[{"role": "system", "content":"Act as an assistant. This is a simple test to see if the API Key works."},
                                                {"role": "user", "content": "Please respond to me by saying 'Hello'."}])
        self.assertTrue(response['choices'][0]['message']['content'])
        if response:
            print(f"\n\nOPENAI_API_KEY Test Response: {response['choices'][0]['message']['content']}")
        else:
            self.fail('There was an issue with retrieving the response back from OpenAI.')


if __name__ == '__main__':
    unittest_main()