from traceback import print_exc


def abs_help():
    try:
        with open("Readme.md", "r") as f:
            text = f.read()

        print(text)
    except Exception as e:
        print_exc()
        print("⚠️ Error while load help")
