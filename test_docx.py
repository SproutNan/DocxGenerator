
    
def fill_applicant_form():
    time_stamp = int(time.time())
    random_num = random.randint(1000,9999)
    template_name = "./template_applicant_form.docx"
    form_name = f"./temp_form_{time_stamp}_{random_num}.docx"
    # fill the template file
    doc = Document(template_name)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if placeholder.act_name in paragraph.text:
                        paragraph.text = paragraph.text.replace(placeholder.act_name, "test_activity_name")
    # save the file
    doc.save(form_name)

if __name__ == "__main__":
    fill_applicant_form()
