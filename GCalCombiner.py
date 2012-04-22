import sys
import json
import ImageDraw
import ImageFont
import Image
import gcal_combiner

def main(path_to_config_json_file):
   '''
     Main function

     Opens json config file and parses.  Creates 
   '''
   config = json.load(open(path_to_config_json_file[0]))

   gcal = gcal_combiner.gcal_combiner(config['num_days_to_search'])

   font_color_map = {}
   for cal in config['Cals']:
      print "Adding: ";
      print  cal
      gcal.addCalendarData(cal['URI_Parms'][0], cal['URI_Parms'][1], cal['cal_name'])
      font_color_map[cal['cal_name']] = cal['font_color']

   gcal.fetchCalendarEvents()

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
   if len(sys.argv) != 2:
      print 'Usage: ./GCalCombiner path_to_config_json_file'
      sys.exit(1)
   #print sys.argv[1:]
   main(sys.argv[1:])