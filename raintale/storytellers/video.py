import logging
import pprint
import tempfile
import imghdr
import io
import math
import textwrap
import os
import shutil

import requests
import requests_cache
import ffmpeg

from PIL import ImageFile, Image, ImageFont, ImageDraw

from .storyteller import FileStoryteller, get_story_elements

module_logger = logging.getLogger('raintale.storytellers.video')

pp = pprint.PrettyPrinter(indent=4)

def save_fading_frames(imbase, im, framesdir, video_width, video_height, frame_width, frame_height, imgcounter,
    archive_favicon_im, original_favicon_im, archive_name, original_domain, memento_datetime, sourcefnt ):
    im_width = im.size[0]
    im_height = im.size[1]

    module_logger.debug("original image size {} x {}".format(im_width, im_height))
    module_logger.debug("video size is {} x {}".format(video_width, video_height))

    if im_width > im_height:
        newwidth = frame_width
        module_logger.debug("resizing height by {}".format((frame_width / im_width)))
        newheight = (frame_width / im_width) * im_height

    elif im_height > im_width:
        newheight = frame_height
        module_logger.debug("resizing width by {}".format((frame_height / im_height)))
        newwidth = (frame_height / im_height) * im_width

    elif im_height == im_width:
        newheight = (frame_width / im_width) * im_height
        newwidth = (frame_height / im_height) * im_width
    
    module_logger.debug("resizing image to {} x {}".format(newwidth, newheight))

    im = im.resize((int(newwidth), int(newheight)), resample=Image.BICUBIC)

    newim = imbase.copy()
    bg_w, bg_h = newim.size

    module_logger.debug("newim size is {} x {}".format(bg_w, bg_h))

    im_width = im.size[0]
    im_height = im.size[1]

    offset = (math.floor((bg_w - im_width) / 2), math.floor((bg_h - im_height) / 2))

    module_logger.info("offset is {}".format(offset))

    newim.paste(im, offset)

    d = ImageDraw.Draw(newim)

    d.rectangle(
        (
            (0, math.floor(frame_height) + 45),
            (video_width, math.floor(frame_height) + 90),
        ),
        fill=(255, 255, 255)
    )

    newim.paste(original_favicon_im, (offset[0], math.floor(frame_height) + 50), )
    newim.paste(
        archive_favicon_im, 
        (offset[0], math.floor(frame_height) + 70), )

    d.text( (offset[0] + 20, math.floor(frame_height) + 45), 
        "{}@{}".format(original_domain, memento_datetime),
        font=sourcefnt, fill=(0, 0, 0) 
        )
    d.text( (offset[0] + 20, math.floor(frame_height) + 65 ), 
        "Preserved by {}".format(archive_name),
        font=sourcefnt, fill=(0, 0, 0) 
        )

    for i in range(1, 99, 10):
        i = i / 100
        imgcounter += 1
        filename = "{}/img{}.png".format(framesdir, str(imgcounter).zfill(10))
        module_logger.debug("saving file to {}".format(filename))
        Image.blend(imbase, newim, i).save(filename)

    for i in range(0, 30):
        imgcounter += 1
        filename = "{}/img{}.png".format(framesdir, str(imgcounter).zfill(10))
        module_logger.debug("saving file to {}".format(filename))
        newim.save(filename)

    for i in range(1, 99, 10):
        i = i / 100
        imgcounter += 1
        filename = "{}/img{}.png".format(framesdir, str(imgcounter).zfill(10))
        module_logger.debug("saving file to {}".format(filename))
        Image.blend(newim, imbase, i).save(filename)

    return imgcounter

class VideoStoryTeller(FileStoryteller):

    description = "(EXPERIMENTAL) Given input data, this storyteller generates a video of fading frames."

    def generate_story(self, story_data, mementoembed_api, story_template):

        module_logger.info("generating story with data: {}".format(story_data))

        requests_cache.install_cache('videostory_test')

        session = requests_cache.CachedSession()

        story_elements = get_story_elements(story_data)

        story_output_data = {
            "title": story_data['title'],
            "generated_by": story_data['generated_by'],
            "collection_url": story_data['collection_url'],
            "elements": []
        }

        for element in story_elements:

            try:

                if element['type'] == 'link':

                    urim = element['value']
                    top_sentence = None
                    top_image_uri = None

                    endpoint = "{}/services/memento/contentdata/{}".format(mementoembed_api, urim)

                    r = session.get(endpoint)

                    module_logger.info("got back a status of {} for {}".format(r.status_code, endpoint))

                    if r.status_code == 200:

                        jdata = r.json()
                        title = jdata["title"]
                        mdt = jdata["memento-datetime"]

                    endpoint = "{}/services/memento/sentencerank/{}".format(mementoembed_api, urim)

                    r = session.get(endpoint)

                    if r.status_code == 200:

                        jdata = r.json()
                        top_sentence = jdata['scored sentences'][0]["text"].replace('\t', ' ').replace('\n', ' ')

                    endpoint = "{}/services/memento/imagedata/{}".format(mementoembed_api, urim)

                    r = session.get(endpoint)

                    if r.status_code == 200:

                        jdata = r.json()
                        top_image_uri = jdata['ranked images'][0]

                    endpoint = "{}/services/memento/originalresourcedata/{}".format(mementoembed_api, urim)

                    r = session.get(endpoint)

                    if r.status_code == 200:

                        jdata = r.json()
                        original_domain = jdata['original-domain']
                        original_favicon = jdata['original-favicon']

                    endpoint = "{}/services/memento/archivedata/{}".format(mementoembed_api, urim)

                    r = session.get(endpoint)

                    if r.status_code == 200:

                        jdata = r.json()
                        archive_name = jdata['archive-name']
                        archive_favicon = jdata['archive-favicon']

                    story_output_data["elements"].append(
                        {
                            "title": title,
                            "text": top_sentence,
                            "memento-datetime": mdt,
                            "original-favicon": original_favicon,
                            "original-domain": original_domain,
                            "archive-favicon": archive_favicon,
                            "archive-name": archive_name
                        }
                    )

                    story_output_data["elements"].append(
                        {
                            "image": top_image_uri,
                            "memento-datetime": mdt,
                            "original-favicon": original_favicon,
                            "original-domain": original_domain,
                            "archive-favicon": archive_favicon,
                            "archive-name": archive_name
                        }
                    )
                
                elif element['type'] == 'text':

                    story_output_data["elements"].append(
                        {
                            "text": element['value'],
                            "image": None
                        }
                    )

                else:
                    module_logger.warning(
                        "element of type {} is unsupported, skipping...".format(element['type'])
                    )

            except KeyError:

                module_logger.exception(
                    "cannot process story element data of {}, skipping".format(element)
                )


        module_logger.debug(
            "story_output_data: {}".format(pprint.pformat(story_output_data))
        )

        return story_output_data


    def publish_story(self, story_output_data):

        module_logger.info("incoming story data:\n{}".format(pprint.pformat(story_output_data, indent=4)))

        requests_cache.install_cache('videostory_test')

        session = requests_cache.CachedSession()

        workingdir = tempfile.mkdtemp(suffix=".tmp", prefix="raintale-")
        # workingdir = "/Users/smj/tmp/raintale-testing"
        framesdir = "{}/videoframes".format(workingdir)

        if not os.path.exists(framesdir):
            os.makedirs(framesdir)

        fontfile = "raintale/fonts/OpenSans-Regular.ttf"

        # 864 x 480 is SD according to https://learn.g2.com/youtube-video-size
        video_height = 480
        video_width = 864

        frame_height = video_height * 0.7
        frame_width = video_width * 0.7

        toptitlefnt = ImageFont.truetype(fontfile, 20)
        metadatafnt = ImageFont.truetype(fontfile, 16)
        sentencefnt = ImageFont.truetype(fontfile, 40)
        sourcefnt = ImageFont.truetype(fontfile, 16)
        imblank = Image.new("RGBA", (video_width, video_height), "black") 
        imbase = Image.new("RGBA", (video_width, video_height), "black")
        d = ImageDraw.Draw(imbase)
        d.text((10, 10), story_output_data["title"], font=toptitlefnt, fill=(255, 255, 255, 255) )
        d.text((30, video_height - 30), "Generated by {}".format(story_output_data["generated_by"]), font=metadatafnt, fill=(255, 255, 255, 255))

        imgcounter = 0
        elementcounter = 0

        for element in story_output_data["elements"]:
            
            elementcounter += 1
            im = None

            module_logger.info("generating video frames for story element {} of {}".format(elementcounter, len(story_output_data["elements"])))

            if "image" in element:

                if element["image"] is not None:

                    r = session.get(element["image"])
                    afav = session.get(element["archive-favicon"])
                    ofav = session.get(element["original-favicon"])
                    if r.status_code == 200 and afav.status_code == 200 and ofav.status_code == 200:
                        imgcounter += 1
                        data = r.content

                        ifp = io.BytesIO(data)
                        im = Image.open(ifp).convert('RGBA', palette=Image.ADAPTIVE)

                        ifp = io.BytesIO(afav.content)
                        ar_favicon_im = Image.open(ifp).convert("RGBA", palette=Image.ADAPTIVE).resize((16, 16), resample=Image.BICUBIC)

                        ifp = io.BytesIO(ofav.content)
                        or_favicon_im = Image.open(ifp).convert("RGBA", palette=Image.ADAPTIVE).resize((16, 16), resample=Image.BICUBIC)

                        imgcounter = save_fading_frames(imbase, im, framesdir, video_width, video_height, 
                            frame_width, frame_height,
                            imgcounter, ar_favicon_im, or_favicon_im, element["archive-name"],
                            element["original-domain"], element["memento-datetime"], sourcefnt)


            if "text" in element:

                afav = session.get(element["archive-favicon"])
                ofav = session.get(element["original-favicon"])
                if afav.status_code == 200 and ofav.status_code == 200:

                    text = element['text']

                    if len(text) > 60:
                        text = '\n'.join(textwrap.wrap(text, width=40))

                    if "title" in element:
                        title = element["title"]

                        if len(title) > 40:
                            title = '\n'.join(textwrap.wrap(title, width=40))

                        text = title + '\n\n' + text

                    im = imblank.copy()
                    d = ImageDraw.Draw(im)
                    module_logger.debug("writing sentence item {}".format(text))

                    ifp = io.BytesIO(afav.content)
                    ar_favicon_im = Image.open(ifp).convert("RGBA", palette=Image.ADAPTIVE).resize((16, 16), resample=Image.BICUBIC)

                    ifp = io.BytesIO(ofav.content)
                    or_favicon_im = Image.open(ifp).convert("RGBA", palette=Image.ADAPTIVE).resize((16, 16), resample=Image.BICUBIC)

                    d.text( (0, 0), text, font=sentencefnt, fill=(255, 255, 255) )

                    imgcounter = save_fading_frames(imbase, im, framesdir, video_width, video_height, 
                        frame_width, frame_height, imgcounter, ar_favicon_im, or_favicon_im, 
                        element["archive-name"], element["original-domain"], element["memento-datetime"], sourcefnt)

        im = imbase.copy()
        d = ImageDraw.Draw(im)
        d.text( (40, 40), "The End", font=sentencefnt, fill=(255, 255, 255))
        imgcounter += 1
        filename = "{}/img{}.png".format(framesdir, str(imgcounter).zfill(10))
        im.save(filename)

        module_logger.info("generating movie from frames")

        if os.path.exists(self.output_filename):
            os.unlink(self.output_filename)

        # outputims = []
        # imout = Image.new("RGBA", (video_width, video_height), "black")

        # for filename in os.listdir(framesdir):            
        #     im = Image.open("{}/{}".format(framesdir, filename))
        #     outputims.append(im)
                

        # with open(self.output_filename, 'wb') as outputfp:
        #     imout.save(
        #         outputfp, save_all=True, format="GIF", 
        #         append_images=outputims, duration=100, loop=0
        #     ) 

        (
            ffmpeg
            .input('{}/img*.png'.format(framesdir), pattern_type='glob', framerate=10)
            .output(self.output_filename, pix_fmt='yuv420p', vcodec='libx264')
            .run()
        )

        shutil.rmtree(workingdir)

        module_logger.info("movie has been saved to {}".format(self.output_filename))

        return self.output_filename
