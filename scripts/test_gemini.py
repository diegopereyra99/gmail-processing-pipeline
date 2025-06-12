from vertexai.preview.generative_models import GenerativeModel

model = GenerativeModel("gemini-2.0-flash")
response = model.generate_content("Summarize: What are the different gemini models")
print(response.text)
