import os
import re
import webbrowser


def generate(data, save_path):
    path = os.path.dirname(__file__)
    template_path = os.path.join(path, "index.php")
    with open(template_path, "r") as template:
        content = template.read()

    php_re = re.compile(r"<\? php \?>", re.S)
    javascript = "const data = '%s';" % data
    content = php_re.sub(javascript, content)

    output = open(save_path, "w+")
    output.write(content)
    output.close()


if __name__ == "__main__":
    input_data = input()

    current_path = os.path.dirname(__file__)
    generated_path = os.path.realpath(os.path.join(current_path, "generated.html"))

    generate(input_data, generated_path)
    webbrowser.open("file://" + generated_path)
