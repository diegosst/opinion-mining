import opinion.extraction.extractor as extractor
import opinion.analysis.analyser as analyser

videos = ['wswb3xhHQmg',
          'GkVwG53bG8I',
          '1elH5B--QO8',
          '2HwFyYIuJuc',
          'cld3NybwVck',
          'TUKF9HUvTOU',
          'yL7xajXpQc4',
          'tYOKR_hpEJ0',
          'wCoTQ6pD4lg']


for code in videos:

    extractor.extract(code)

analyser.analyse('FMNfdQAJM2A')


