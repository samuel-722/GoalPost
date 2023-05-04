from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import re
from pdfminer.high_level import extract_text
from collections import deque

class AssistParser:
    def __init__(self, file_name):
        self.file_name = file_name  # name of document with .pdf at the end
        self.dict = {} # university is key college is value
        self.q = deque()    # queue to process classes 
        self.university_pattern = re.compile("[A-Z]{2,5}\s\d{1,5}[A-Z]?\s-\s(.*){5,80}\(.{4}\)") # regex for university courses
        self.college_pattern = re.compile("←\s[A-Z]{2,5}\s\d{1,5}[A-Z]?\s-\s(.*){5,80}\(.{4}\)") # regex for college courses

    def extract_text(self):
        return extract_text(self.file_name) # get the name of the file

    def prepare_text(self):
        text = self.extract_text()
        unicode_removedText = text.replace('\u200b', '')
        text_to_erase = re.split(self.university_pattern, unicode_removedText, maxsplit = 1)[0]
        essential_text = unicode_removedText.partition(text_to_erase)[2]
        newline_removedText = essential_text.replace('\n','')
        additional_newLine_Text = re.sub(r"(\(\d\.\d0\))", r"\1\n", newline_removedText)
        ready_text = re.sub(r"(\.*)([←\s]*[A-Z]{2,5}\s\d{1,5}[A-Z]?\s-\s(.*){5,80}\(.{4}\))", r"\1\n\2", additional_newLine_Text)
        ready_text = ready_text.replace("\n\n", "\n").strip()
        
        parts = ready_text.split("\n")
        merged_parts = []
        current_part = 0
        while current_part < len(parts):
            if (current_part + 2 < len(parts) and "--- And ---" in parts[current_part + 1]):
                merged_parts.append(parts[current_part] + parts[current_part + 1] + parts[current_part + 2])
                current_part+=3
            elif (current_part + 2 < len(parts) and "--- Or ---" in parts[current_part + 1]):
                merged_parts.append(parts[current_part] + parts[current_part + 1] + parts[current_part + 2])
                current_part+=3
            else:
                merged_parts.append(parts[current_part])
                current_part+=1
        return "\n".join(merged_parts)
    
    def process_dict(self, ready_text):
        for line in ready_text.split('\n'):
            if self.college_pattern.search(line):
                self.dict[self.q.popleft()] = line[2:]      
            elif self.university_pattern.search(line):
                self.q.append(line)
            elif "No Course Articulated" in line:
                self.dict[self.q.popleft()] = line[2:]

    def parse(self):
        ready_text = self.prepare_text()
        self.process_dict(ready_text)
        return self.dict
    
# Create your views here.
def index(request):
    template = loader.get_template('index.html')
    parser = AssistParser("Assist_SFState.pdf")
    classes = parser.parse()
    context = {'my_dict': classes}
    return HttpResponse(template.render(context, request))