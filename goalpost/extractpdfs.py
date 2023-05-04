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


        # merged_text = ""
        # previous_line = ""
        # line_before_previous = ""
        # ready_text = ready_text.replace("\n\n", "\n").strip()
        # for line in ready_text.split("\n"):
        #     if "--- And ---" in line:
        #         merged_line = line_before_previous.strip() + " AND " + previous_line.strip() + "\n"
        #         merged_text += merged_line + "\n"
        #         previous_line = ""
        #         line_before_previous = ""    
        #     elif "--- Or ---" in line:
        #         merged_line = line_before_previous.strip() + " Or " + previous_line.strip() + "\n"
        #         merged_text += merged_line + "\n"
        #         previous_line = ""
        #         line_before_previous = ""
        #     elif line == ready_text.split("\n")[-1]:
        #         merged_text += line_before_previous + "\n" + previous_line + "\n" + line + "\n"
        #     else:
        #         merged_text += line_before_previous + "\n"
        #         line_before_previous = previous_line
        #         previous_line = line
        # ready_text = merged_text.strip()

        return ready_text
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
    
def main():
    parser = AssistParser("Assist_Davis.pdf")
    classes = parser.parse()
    return classes

if __name__ == "__main__":
    main()