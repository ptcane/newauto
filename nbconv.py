from nbconvert import MarkdownExporter
import re
from glob import glob
from markdown import markdown
import subprocess
from shutil import copytree, rmtree
from os import remove

md_exclusions = []

nb_static_dir = "nb_output"
nb_template_dir = "nb_html"
nb_dir = "notebooks"


img_source_dir = r"notebooks/images/"
img_target_dir = r"nb_images/"

copytree(img_source_dir, img_target_dir, dirs_exist_ok=True)

nbs = glob(rf"{nb_dir}/*.ipynb")
md_nbs = [nb for nb in nbs if nb not in md_exclusions]
print(md_nbs)

for nb in md_nbs:

    nb_name = nb[len(nb_dir) + 1 : -6]

    command = rf"jupyter nbconvert {nb} --to markdown"
    subprocess.run(command, stdout=subprocess.DEVNULL)

    try:
        copytree(
            f"{nb_dir}/{nb_name}_files",
            f"{nb_static_dir}/{nb_name}",
            dirs_exist_ok=True,
        )

        rmtree(f"{nb_dir}/{nb_name}_files")

    except:
        pass


# markdown
regex = re.compile(r"```(\n)+((\ {4,}?.+((\n| )+))+)\n")
prefix = "\n\n```{.python .nb-output}\n"
suffix = "\n```\n\n"
prefix_offset = 3
suffix_offset = 0
max_matches = None
start_index = 0

for nb in md_nbs:

    nb_name = nb[10:-6]
    html_file_dest = f"{nb_template_dir}/{nb_name}.html"
    md_file = f"{nb_dir}/{nb_name}.md"

    with open(f"{md_file}", "r") as f:
        text = f.read()

    remove(md_file)

    matches = re.finditer(regex, text)

    locations = []
    for match in matches:
        start = match.start()
        end = match.end()
        locations.append((start, end))

    destinations = [
        (location[0] + prefix_offset, location[1] + suffix_offset)
        for location in locations
    ][:max_matches]

    new = []

    text_pos = start_index
    for dest in destinations:
        prefix_pos = dest[0]
        suffix_pos = dest[1]
        replacement_string = text[prefix_pos:suffix_pos].strip(
            "\n"
        )  # specific to this scenario
        new.append(f"{text[text_pos:prefix_pos]}{prefix}{replacement_string}{suffix}")
        text_pos = suffix_pos
    new.append(text[text_pos:])

    print(f"{len(destinations)} regex matches processed.")

    new_text = "".join(new)

    html = markdown(new_text, extensions=["fenced_code"])

    html = html.replace(
        rf'img alt="png" src="{nb_name}_files',
        rf'img alt="png" src="/wp-content/uploads/nb_output/{nb_name}',
    )

    html = html.replace(
        r'src="images/',
        r'src="/wp-content/uploads/nb_images/',
    )

    with open(rf"{nb_template_dir}/{nb_name}.html", "w+") as f:

        f.write(html)
