import os
import re
import json
import yaml
import codecs
import urllib.request
from pathlib import Path

import requests
import sparkline
import prettytable
from bs4 import BeautifulSoup


cookies = {
'__cfduid': 'df900a5c62717d85402c108339e9222101619198063',
'cf_chl_2': 'cd1eeb4ead9a261',
'cf_chl_prog': 'x10',
'cf_clearance': '15745c5c29a851c0328603a11a58fd7510dba420-1619198063-0-150',
'DO-LB': 'node-219053868|YIMA1|YIMAc',
}

headers = {
'Host': 'tryhackme.com',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Content-Type': 'application/json;charset=utf-8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate',
'Connection': 'close',
'Upgrade-Insecure-Requests': '1',
'If-None-Match': 'W/\\"1455-mqO5367pbx4mk/5e4eVCOzEr1xo\\"',
'Cache-Control': 'max-age=0',
}

def highlight(text, color="black", bold=False):
  resetcode = "\x1b[0m"
  color = color.lower().strip()
  if color == "black":
    colorcode = "\x1b[0;30m" if not bold else "\x1b[1;30m"
  elif color == "white":
    colorcode = "\x1b[0;37m" if not bold else "\x1b[1;37m"
  elif color == "red":
    colorcode = "\x1b[0;31m" if not bold else "\x1b[1;31m"
  elif color == "green":
    colorcode = "\x1b[0;32m" if not bold else "\x1b[1;32m"
  elif color == "yellow":
    colorcode = "\x1b[0;33m" if not bold else "\x1b[1;33m"
  elif color == "blue":
    colorcode = "\x1b[0;34m" if not bold else "\x1b[1;34m"
  elif color == "magenta":
    colorcode = "\x1b[0;35m" if not bold else "\x1b[1;35m"
  elif color == "cyan":
    colorcode = "\x1b[0;36m" if not bold else "\x1b[1;36m"
  else:
    colorcode = "\x1b[0;30m" if not bold else "\x1b[1;30m"
  return "%s%s%s" % (colorcode, text, resetcode)

def black(text):
  return highlight(text, color="black", bold=False)

def black_bold(text):
  return highlight(text, color="black", bold=True)

def white(text):
  return highlight(text, color="white", bold=False)

def white_bold(text):
  return highlight(text, color="white", bold=True)

def red(text):
  return highlight(text, color="red", bold=False)

def red_bold(text):
  return highlight(text, color="red", bold=True)

def green(text):
  return highlight(text, color="green", bold=False)

def green_bold(text):
  return highlight(text, color="green", bold=True)

def yellow(text):
  return highlight(text, color="yellow", bold=False)

def yellow_bold(text):
  return highlight(text, color="yellow", bold=True)

def blue(text):
  return highlight(text, color="blue", bold=False)

def blue_bold(text):
  return highlight(text, color="blue", bold=True)

def magenta(text):
  return highlight(text, color="magenta", bold=False)

def magenta_bold(text):
  return highlight(text, color="magenta", bold=True)

def cyan(text):
  return highlight(text, color="cyan", bold=False)

def cyan_bold(text):
  return highlight(text, color="cyan", bold=True)

def debug(text):
  print("%s %s" % (blue_bold("[*]"), text))

def info(text):
  print("%s %s" % (green_bold("[+]"), text))

def warn(text):
  print("%s %s" % (yellow_bold("[!]"), text))

def error(text):
  print("%s %s" % (red_bold("[-]"), text))

def expand_env(var="$HOME"):
  return os.environ[var.replace("$", "")]

def trim(text, maxq=40):
  text = text.strip()
  return "%s%s" % (text[:maxq].strip(), black("...")) if len(text) > maxq else text

def download_json(url):
  with urllib.request.urlopen(url) as url:
    return json.loads(url.read().decode())

def load_json(filename):
  fileobj = Path(filename)
  if fileobj.is_file():
    with open(filename) as fp:
      return json.load(fp)

def save_json(datadict, filename):
  with open(filename, "w", encoding="utf-8") as fp:
    json.dump(datadict, fp, ensure_ascii=False, indent=2, sort_keys=True)

def load_file(filename):
  lines = []
  fileobj = Path(filename)
  if fileobj.is_file():
    with open(filename) as fp:
      lines = sorted(list(set(list(list(filter(None, fp.read().split("\n")))))))
  return lines

def save_file(datalist, filename):
  with open(filename, "w") as fp:
    fp.write("\n".join(sorted(list(set(list(list(filter(None, datalist))))))))
    fp.write("\n")

def load_yaml(filename):
  fileobj = Path(filename)
  if fileobj.is_file():
    return yaml.safe_load(open(filename))

def save_yaml(datayml, filename):
  with open(filename, "w") as fp:
    yaml.dump(datayml, fp, default_flow_style=True)

def dict2yaml(datadict):
  return yaml.safe_dump(yaml.load(json.dumps(datadict), Loader=yaml.FullLoader), default_flow_style=False)

def file_open(filename):
  if filename and filename != "":
    with codecs.open(filename, mode="r", encoding="utf-8") as fo:
      return fo.read()

def file_save(filename, data, mode="w"):
  if filename and filename != "":
    if "/" in filename:
      mkdirp(os.path.dirname(filename))
    try:
      with codecs.open(filename, mode, encoding="utf-8") as fo:
        fo.write(data)
    except Exception as ex:
      with open(filename, mode) as fo:
        try:
          fo.write(data)
        except:
          fo.write(data.encode('utf-16', 'surrogatepass').decode('utf-16'))

def download(url, filename):
  res = requests.get(url)
  if res.status_code == 200:
    open(filename, "wb").write(res.content)

def get_http_res(url, headers={}, requoteuri=False):
  if requoteuri:
    return requests.get(cleanup_url(requests.utils.requote_uri(url)), headers=headers, cookies=cookies)
  else:
    return requests.get(cleanup_url(url), headers=headers, cookies=cookies)

def get_http(url, headers={}, session=None):
  if session:
    res = session.get(cleanup_url(url), headers=headers, cookies=cookies)
  else:
    res = requests.get(cleanup_url(url), headers=headers, cookies=cookies)
  if res.status_code == 200:
    return res.json()
  else:
    return {}


def get_bypassed_http(url):


  cookies = {
    '__cfduid': 'df900a5c62717d85402c108339e9222101619198063',
    'cf_chl_2': 'cd1eeb4ead9a261',
    'cf_chl_prog': 'x10',
    'cf_clearance': '15745c5c29a851c0328603a11a58fd7510dba420-1619198063-0-150',
    'DO-LB': 'node-219053868|YIMA1|YIMAc',
  }

  headers = {
    'Host': 'tryhackme.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1',
    'If-None-Match': 'W/\\"1455-mqO5367pbx4mk/5e4eVCOzEr1xo\\"',
    'Cache-Control': 'max-age=0',
  }

  response = requests.get(url, headers=headers, cookies=cookies)
  if response.status_code == 200:
    return response.json()
  else:
    return {}


def post_http(url, data={}, headers={}, session=None):
  if session:
    res = session.post(cleanup_url(url), data=json.dumps(data), headers=headers, cookies=cookies)
  else:
    res = requests.post(cleanup_url(url), data=json.dumps(data), headers=headers, cookies=cookies)
  if res.status_code == 200:
    return res.json()
  else:
    return {}

def strip_html(data):
  return re.sub("\s+", " ", BeautifulSoup(data, "lxml").text)

def cleanup_url(url):
  return url.replace("//", "/").replace(":/", "://")

def cleanup_name(name):
  return re.sub(r"[\W_]", "", name.lower())
  return name.lower().replace(" ", "").replace(":", "").replace("_", "").replace("-", "")

def yturl2verboseid(url):
  v, t = None, None
  for param in url.strip().split("?", 1)[1].split("&"):
    if param.startswith("v="):
      v = param.split("=")[1]
    if param.startswith("t="):
      t = param
  if v and t:
    return "youtu.be/%s?%s" % (v, t)
  elif v:
    return "youtu.be/%s" % (v)
  else:
    return url

def sparkify(difficulty):
  return sparkline.sparkify(difficulty)

def to_color_difficulty(sparkline):
  return "".join([green(sparkline[:3]), yellow(sparkline[3:7]), red(sparkline[7:])])

def to_emoji(text):
  text = str(text)
  # https://github.com/ikatyang/emoji-cheat-sheet
  if "private" == text.lower():
    return red("") # 
  elif "public" == text.lower():
    return green("")
  elif "oscplike" == text.lower():
    return magenta("")
  elif "access_root" == text.lower():
    return red("")
  elif "access_user" == text.lower():
    return yellow("")
  elif "has_writeup" == text.lower():
    return yellow("")
  elif "android" in text.lower():
    return green("")
  elif "arm" in text.lower():
    return magenta("")
  elif "bsd" in text.lower():
    return red("")
  elif "linux" == text.lower():
    return yellow("")
  elif "solaris" in text.lower():
    return magenta("")
  elif "unix" in text.lower():
    return magenta("")
  elif "windows" == text.lower():
    return blue("")
  elif "other" in text.lower():
    return magenta("")
  elif "difficulty_unknown" == text.lower():
    return ""
  elif "easy" == text.lower():
    return white("")
  elif "medium" == text.lower():
    return green("")
  elif "hard" == text.lower():
    return yellow("")
  elif "insane" == text.lower():
    return red("")
  else:
    return ""

def to_markdown_table(pt):
  _junc = pt.junction_char
  if _junc != "|":
    pt.junction_char = "|"
  markdown = [row for row in pt.get_string().split("\n")[1:-1]]
  pt.junction_char = _junc
  return "\n".join(markdown)

def get_table(header, rows, delim="___", aligndict=None, markdown=False, colalign=None, multiline=False):
  table = prettytable.PrettyTable()
  table.field_names = header
  table.align = "c"; table.valign = "m"
  for row in rows:
    table.add_row(row.split(delim))
  if markdown:
    if colalign in ["left", "center", "right"]:
      if colalign == "left":
        return to_markdown_table(table).replace("|-", "|:")
      elif colalign == "center":
        return to_markdown_table(table).replace("-|-", ":|:").replace("|-", "|:").replace("-|", ":|")
      elif colalign == "right":
        return to_markdown_table(table).replace("-|", ":|")
    else:
      #return table.get_html_string()
      return to_markdown_table(table)
  else:
    if aligndict:
      for colheader in aligndict:
        table.align[colheader] = aligndict[colheader]
    else:
      table.align["#"] = "r"
      table.align["ID"] = "r"
      table.align["Name"] = "l"
      table.align["Expires"] = "l"
      table.align["Match"] = "l"
      table.align["Follow"] = "l"
      table.align["Private"] = "c"
      table.align["Rating"] = "c"
      table.align["Difficulty"] = "c"
      table.align["OS"] = "c"
      table.align["OSCPlike"] = "c"
      table.align["Owned"] = "c"
      table.align["Writeup"] = "c"
      table.align["TTPs"] = "c"
    table.vertical_char = " "
    table.horizontal_char = "-"
    table.junction_char = " "
    table.hrules = prettytable.ALL if multiline else prettytable.FRAME
    return "\n%s\n" % (table.get_string())

def to_table(header, rows, delim="___", aligndict=None, markdown=False, multiline=False):
  print(get_table(header, rows, delim=delim, aligndict=aligndict, markdown=markdown, multiline=multiline))

def to_json(data):
  print(json.dumps(data, indent=2, sort_keys=True))

def to_gsheet(data):
  lines = []
  for item in data:
    name = "=HYPERLINK(\"%s\",\"%s\")" % (item["url"], item["name"])
    if "htb" in item["infrastructure"] or "hackthebox" in item["infrastructure"]:
      infra = "HackTheBox"
    elif "vh" in item["infrastructure"] or "vulnhub" in item["infrastructure"]:
      infra = "VulnHub"
    elif "thm" in item["infrastructure"] or "tryhackme" in item["infrastructure"]:
      infra = "TryHackMe"
    else:
      infra = "Misc"
    os = item["os"].title()
    points = item["points"] if item["points"] else ""
    owned = "Yes" if item["owned_user"] or item["owned_root"] else "No"
    lines.append("%s,%s,%s,%s,%s," % (name, infra, os, points, owned))
  print("Name,Infra,OS,Points,Difficulty,Owned,Writeup")
  for line in sorted(lines):
    print(line)

def show_machines(data, sort_key="name", jsonify=False, gsheet=False, showttps=False):
  if not len(data):
    return
  elif "success" in data:
    return to_json(data)
  elif jsonify:
    to_json(data)
  elif gsheet:
    to_gsheet(data)
  else:
    rows = []
    if data[0].get("expires_at"):
      header = ["#", "ID", "Name", "Expires", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup", "TTPs"] if showttps else ["#", "ID", "Name", "Expires", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = trim(entry["name"], maxq=30)
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        writeup = to_emoji("has_writeup") if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        ttps = "\n".join([
          ",".join([green(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["enumerate"]]),
          ",".join([yellow(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["exploit"]]),
          ",".join([red(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["privesc"]])
          ]).strip() if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        if showttps:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            entry["expires_at"],
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
            ttps,
          ))
        else:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            entry["expires_at"],
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
          ))

    elif data[0].get("search_url"):
      header = ["#", "ID", "Name", "Follow", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup", "TTPs"] if showttps else ["#", "ID", "Name", "Follow", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = trim(entry["name"], maxq=30)
        match = trim(entry["search_text"].replace(" - ", " ").strip(), maxq=30) if entry.get("search_text") else ""
        if entry["search_url"].startswith("youtu.be/"):
          follow = "%s %s" % (red(""), blue(entry["search_url"]))
        else:
          follow = blue(entry["search_url"])
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        writeup = to_emoji("has_writeup") if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        ttps = "\n".join([
          ",".join([green(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["enumerate"]]),
          ",".join([yellow(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["exploit"]]),
          ",".join([red(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["privesc"]])
          ]).strip() if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        if showttps:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            follow,
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
            ttps,
          ))
        else:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            follow,
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
          ))

    else:
      header = ["#", "ID", "Name", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup", "TTPs"] if showttps else ["#", "ID", "Name", "Rating", "Difficulty", "OS", "OSCPlike", "Owned", "Writeup"]
      for idx, entry in enumerate(sorted(data, key=lambda k: k[sort_key].lower())):
        mid = "%s%s" % (blue("%s#" % (entry["verbose_id"].split("#")[0])), blue_bold("%s" % (entry["verbose_id"].split("#")[1])))
        name = trim(entry["name"], maxq=30)
        os = to_emoji(entry["os"])
        difficulty = entry["difficulty"] if entry.get("difficulty") and entry["difficulty"] else "difficulty_unknown"
        rating = to_color_difficulty(sparkify(entry["difficulty_ratings"])) if entry.get("difficulty_ratings") else ""
        oscplike = "oscplike" if entry.get("oscplike") and entry["oscplike"] else "notoscplike"
        if entry.get("owned_root") and entry["owned_root"]:
          owned = "access_root"
        elif entry.get("owned_user") and entry["owned_user"]:
          owned = "access_user"
        else:
          owned = "access_none"
        writeup = to_emoji("has_writeup") if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        ttps = "\n".join([
          ",".join([green(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["enumerate"]]),
          ",".join([yellow(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["exploit"]]),
          ",".join([red(x) for x in entry["writeups"]["7h3rAm"]["ttps"]["privesc"]])
          ]).strip() if entry.get("writeups") and entry["writeups"].get("7h3rAm") else ""
        if showttps:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
            ttps,
          ))
        else:
          rows.append("%s.___%s___%s___%s___%s___%s___%s___%s___%s" % (
            idx+1,
            mid,
            name,
            rating,
            to_emoji(difficulty),
            os,
            to_emoji(oscplike),
            to_emoji(owned),
            writeup,
          ))

    to_table(header=header, rows=rows, delim="___", aligndict=None, markdown=False, multiline=False)
