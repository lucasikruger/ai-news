import sys
sys.path.append('..')
from src.content_provider import PapersWithCodeContentProvider

def main():
    contentProvider = PapersWithCodeContentProvider()
    content = contentProvider.get_content()
    for paper in content:
        print(paper)
        print("\n")

if __name__ == "__main__":
    main()