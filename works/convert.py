import json
import os
import glob
import re

all_data = []

LOLITA_CHAPTERS = {
	"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
	"eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
	"eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three",
	"twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight",
	"twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three",
}

def normalize_whitespace(text):
	return " ".join(text.split())


def looks_like_title_heading(line):
	words = line.split()
	if not words or len(words) > 8 or len(line) > 60:
		return False
	if line[0] in '["\'((' or line[-1] in ']"\')' or line[-1] in ".,;:!?":
		return False
	if re.search(r"[\[\]\(\)\{\}.,;:!?\"']", line):
		return False
	minor_words = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}
	for word in words:
		clean_word = re.sub(r"[^A-Za-z0-9']", "", word)
		if not clean_word:
			continue
		if clean_word.lower() in minor_words:
			continue
		if clean_word[0].isupper() or clean_word.isupper():
			continue
		return False
	return True


def heading_info(line, title):
	normalized = normalize_whitespace(line)
	lower = normalized.lower()
	is_lath = title == "LATH"
	is_lolita = title == "LOLITA"

	if re.match(r"^part\s+(one|two|three|four|five|six|seven|eight|nine|ten|[ivxlcdm]+|\d+)\b", normalized, re.IGNORECASE):
		return normalized, 1

	if is_lolita:
		if lower in LOLITA_CHAPTERS:
			return normalized, 2
		if re.match(r"^(foreword|afterword)\b", normalized, re.IGNORECASE):
			return normalized, 1
		return None

	if is_lath:
		if re.match(r"^\d+$", normalized):
			return normalized, 2
		if re.match(r"^(commentary)\b", normalized, re.IGNORECASE):
			return normalized, 1
		return None

	if re.match(r"^(chapter|canto|section)\b", normalized, re.IGNORECASE):
		return normalized, 2

	if re.match(r"^(commentary|foreword|introduction|dedication|poem|epigraph|prologue|epilogue|contents|cover|title page|copyright|other books by this author|other books by the narrator)\b", normalized, re.IGNORECASE):
		return normalized, 1

	if re.match(r"^(line|lines)\s+\d+", normalized, re.IGNORECASE):
		return normalized, 3

	if re.match(r"^\d+$", normalized):
		return normalized, 2

	if re.match(r"^\d+\s+[A-Z]", normalized):
		return normalized, 1

	if re.match(r"^[IVXLCDM]+$", normalized):
		return normalized, 3

	if looks_like_title_heading(normalized):
		return normalized, 1

	return None


def push_heading(stack, heading_label, heading_rank):
	while stack and stack[-1][0] >= heading_rank:
		stack.pop()
	stack.append((heading_rank, heading_label))


def current_structure(stack):
	return " / ".join(label for _, label in stack)


def flush_buffer(buffer, stack, title):
	text = normalize_whitespace(" ".join(buffer))
	if text:
		all_data.append({
			"title": title,
			"structure": current_structure(stack),
			"text": text,
		})


def process_file(filename):
	print(f"Reading {filename}...")
	stack = []
	buffer = []
	title = filename.replace(".txt", "").upper()
	outer_pale_fire_heads = {"foreword", "commentary", "canto i", "canto ii", "canto iii", "canto iv"}

	with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
		for raw_line in f.read().splitlines():
			line = raw_line.strip()
			if not line:
				flush_buffer(buffer, stack, title)
				buffer = []
				continue

			heading = heading_info(line, title)
			if heading:
				flush_buffer(buffer, stack, title)
				buffer = []
				if title == "PALEFIRE" and re.match(r"^lines?\b", heading[0], re.IGNORECASE):
					while stack and stack[-1][0] == 1 and stack[-1][1].lower() not in outer_pale_fire_heads:
						stack.pop()
				push_heading(stack, heading[0], heading[1])
				continue

			buffer.append(line)

	flush_buffer(buffer, stack, title)

# This looks for ANY .txt file in the same folder as the script
files = glob.glob("*.txt")

if not files:
	print("Error: I still can't see any .txt files. Are they in this folder?")
	print(f"Current Directory: {os.getcwd()}")
else:
	for filename in files:
		process_file(filename)

	# Save the data.js file
	with open('data.js', 'w', encoding='utf-8') as out:
		out.write("const nabokovWorks = " + json.dumps(all_data) + ";")

	print(f"\nSuccess! Created data.js with {len(all_data)} entries.")
	print("Now open your index.html file to search.")