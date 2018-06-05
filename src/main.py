import opinion.extraction.extractor as extractor
import opinion.analysis.analyser as analyser


# YouTube video codes used for extracting features.
videos = ['wswb3xhHQmg',
          'GkVwG53bG8I',
          '1elH5B--QO8',
          '2HwFyYIuJuc',
          'cld3NybwVck',
          'TUKF9HUvTOU',
          'yL7xajXpQc4',
          'tYOKR_hpEJ0',
          'wCoTQ6pD4lg',
          'ynPFhR3DzFk',
          'FMNfdQAJM2A']


for code in videos:

    extractor.extract(code)

# YouTube video code used for analysing.
analyser.analyse('xEU-aft-bzg')


