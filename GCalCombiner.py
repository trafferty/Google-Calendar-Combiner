import sys
import json
from PIL import ImageDraw
from PIL import ImageFont
from PIL import Image
import gcal_combiner

def main(argv):
    '''
     Main function

     argv[1] = path_to_config_json_file path_to_client_secrets_file
    '''
    config = json.load(open(argv[1]))
    path_to_discovery_file = argv[2]

    # create calendar combiner
    gcal = gcal_combiner.gcal_combiner()

    font_color_map = {}
    for cal in config['Cals']:
        print "Adding: ";
        print  cal
        gcal.addCalendarData(cal['cal_id'], cal['cal_name'])
        font_color_map[cal['cal_name']] = cal['font_color']

    gcal.fetchCalendarEvents(config['num_days_to_search'], path_to_discovery_file)

    linesToPrint = gcal.buildLinesToPrint()

    # load the font
    print "Loading font: %s" % config['font_path']
    arialFont  =  ImageFont.truetype ( config['font_path'], 16)

    # num lines to print
    numLinesToPrint = len(linesToPrint)

    for image in config['Images']:
        width  = image['width']
        height = image['height']

        if not isinstance(height, int):
            height = (numLinesToPrint * config['y_pitch'] + 5)

        # create an image object
        im = Image.new("RGB", (width, height), "rgb(215,215,215)")

        # extract a draw object for images
        draw_object = ImageDraw.Draw(im)

        # starting at the top, write out each line in the desired color 
        idx = 0
        for lineToPrint in linesToPrint:
            y_loc = 2 + (idx * config['y_pitch'])
            draw_object.text((2,y_loc), lineToPrint[0], font_color_map[lineToPrint[1]], arialFont)
            idx+=1

        print "Saving cal image to %s" % image['path']
        im.save(image['path'])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ./GCalCombiner path_to_config_json_file path_to_discovery_file'
        sys.exit(1)
    #print sys.argv[1:]
    main(sys.argv)