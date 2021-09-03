from PIL import Image, ImageDraw
import numpy as np
import wcag_contrast_ratio as contrast

class DiamondPaintingGeneratorLogic:
    def __init__(self):
        self.pixelPalette = {}
        self.alphabetImagesPreGenerated = {}
        self.possibleColorValuesForAlpha = []

    @staticmethod
    def loadImage(path, max_size):
        src_img = Image.open(path)
        if src_img.width > max_size > 0:
            src_img = src_img.resize((max_size, int(max_size * (src_img.height / src_img.width))), 0)
        return src_img

    def alphaProcess(self, input_image):
        pixel_array = np.array(input_image)
        self.pixelPalette = {}
        pixel_index = 0

        for x in pixel_array:
            for a in x:
                col_str = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0], a[1], a[2], a[3])
                if col_str not in self.pixelPalette:
                    self.pixelPalette[col_str] = str(pixel_index)
                    pixel_index = pixel_index + 1

    @staticmethod
    def set_image_dpi_in_memory(image):
        length_x, width_y = image.size
        factor = min(1, float(1024.0 / length_x))
        size = int(factor * length_x), int(factor * width_y)
        image_resize = image.resize(size, Image.ANTIALIAS)
        return image_resize

    @staticmethod
    def generateLetterImage(letter, color, round_shape, diamond_size, font, outlineWidth):
        output_picture = Image.new('RGBA', (diamond_size+2, diamond_size+2))
        output_picture_drawing_context = ImageDraw.Draw(output_picture)
        output_picture_drawing_context.rectangle((0, 0, diamond_size+2, diamond_size+2), fill=(255, 255, 255, 0))
        inverted_color = (255 - color[0], 255 - color[1], 255 - color[2])
        inv_color_range = (inverted_color[0]/255,inverted_color[1]/255,inverted_color[2]/255)
        color_range = (color[0]/255,color[1]/255,color[2]/255)
        if not contrast.passes_AA(contrast.rgb(inv_color_range, color_range)):
            if not contrast.passes_AA(contrast.rgb((1,1,1), color_range)):
                inverted_color = (0,0,0)
            else:
                inverted_color = (255,255,255)

        if round_shape:
            output_picture_drawing_context.ellipse(((0, 0), (diamond_size, diamond_size)),
                                                   (color[0], color[1], color[2]),
                                                   (0, 0, 0), width=outlineWidth)
        else:
            output_picture_drawing_context.rectangle(((0, 0), (diamond_size, diamond_size)),
                                                     (color[0], color[1], color[2]), (0, 0, 0)
                                                     , width=outlineWidth)
        output_picture_drawing_context.text((0 + (diamond_size / 2), 0 + (diamond_size / 2)),
                                            letter, inverted_color, font=font, anchor="mm")
        return output_picture

    def generateDiamondPainting(self, input_image, alphabet, alpha_color, font, diamond_size, round_diamonds, space_between, outlineWidth):
        input_array = np.array(input_image)
        self.pixelPalette.clear()
        input_index = 0
        new_image = Image.new('RGB', (input_image.size[0] * (diamond_size + space_between + 1), input_image.size[1] * (diamond_size + space_between + 1)))

        new_image_draw_context = ImageDraw.Draw(new_image)
        new_image_draw_context.rectangle((0, 0,
                                          input_image.size[0] * (diamond_size + space_between + 1), input_image.size[1] * (diamond_size + space_between + 1)),
                                         fill=(255, 255, 255))

        self.alphabetImagesPreGenerated.clear()

        y_count = 0
        for x in input_array:
            x_count = 0
            for a in x:
                col_str = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0], a[1], a[2], a[3])
                colour = "%0.2X%0.2X%0.2X" % (a[0], a[1], a[2])
                if colour in self.pixelPalette:
                    out = self.pixelPalette[colour]
                else:
                    self.pixelPalette[colour] = str(input_index)
                    input_index = input_index + 1
                    out = self.pixelPalette[colour]
                out = alphabet[int(out)]

                if out in self.alphabetImagesPreGenerated:
                    out_img = self.alphabetImagesPreGenerated[out]
                else:
                    self.alphabetImagesPreGenerated[out] = self.generateLetterImage(out,
                                                                                    a,
                                                                                    round_diamonds,
                                                                                    diamond_size,
                                                                                    font,
                                                                                    outlineWidth)
                    out_img = self.alphabetImagesPreGenerated[out]

                if (a[3] != 0) and (col_str != alpha_color):
                    new_image.paste(out_img, box=(x_count * (diamond_size + space_between), y_count * (diamond_size + space_between)))

                x_count = x_count + 1
            y_count = y_count + 1

        return new_image #self.set_image_dpi_in_memory(new_image)

    @staticmethod
    def autocrop(image):
        image_data = np.asarray(image)
        image_data_bw = image_data.max(axis=2, initial=0)
        non_empty_columns = np.where(image_data_bw.min(axis=0) < 255)[0]
        non_empty_rows = np.where(image_data_bw.min(axis=1) < 255)[0]
        crop_box = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

        image_data_new = image_data[crop_box[0]:crop_box[1] + 1, crop_box[2]:crop_box[3] + 1, :]

        new_image = Image.fromarray(image_data_new)
        return new_image

    def generateTable(self, fnt, alphabet, diamond_shape_size, alphaColor):
        tab_dim = (1000, 1000)
        new_image = Image.new('RGBA', tab_dim)
        new_image_draw_context = ImageDraw.Draw(new_image)
        new_image_draw_context.rectangle((0, 0, tab_dim[0], tab_dim[1]), fill=(255, 255, 255))

        x_width = 200
        x_left = diamond_shape_size + 6
        y_pos = 0
        y_height = diamond_shape_size + 6

        new_image_draw_context.rectangle((0, y_pos, x_width, y_pos + y_height), fill=None, outline=(0, 0, 0))
        new_image_draw_context.rectangle((0, y_pos, x_left, y_pos + y_height), fill=None, outline=(0, 0, 0))
        new_image_draw_context.text((int(x_left/2), int(y_height/2)), "@", (0, 0, 0), font=fnt, anchor="mm")
        new_image_draw_context.text((x_left + 4, int(y_height/2)), "Color Code", (0, 0, 0), font=fnt, anchor="lm")

        
        y_pos = y_pos + y_height
        for colour in self.pixelPalette:
            if colour == alphaColor[1:7].upper():
                continue

            new_image_draw_context.rectangle((0, y_pos, x_width, y_pos + y_height),
                                             fill=None, outline=(0, 0, 0))
            new_image_draw_context.rectangle((0, y_pos, x_left, y_pos + y_height),
                                             fill="#" + colour, outline=(0, 0, 0))

            out = self.pixelPalette[colour]
            out = alphabet[int(out)]
            out_img = None
            if out in self.alphabetImagesPreGenerated:
                out_img = self.alphabetImagesPreGenerated[out]
            new_image.paste(out_img, box=(3, int(y_pos)+3), mask=out_img)

            new_image_draw_context.text((x_left + 4, y_pos + y_height / 2),
                                        "#" + colour, (0, 0, 0), font=fnt, anchor="lm")
            y_pos = y_pos + y_height
        new_image = self.autocrop(new_image.convert("RGB"))
        return new_image

#
# const getLuminanace = (values) => {
#   const rgb = values.map((v) => {
#     const val = v / 255;
#     return val <= 0.03928 ? val / 12.92 : ((val + 0.055) / 1.055) ** 2.4;
#   });
#   return Number((0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]).toFixed(3));
# };
#
# const getContrastRatio = (colorA, colorB) => {
#   const lumA = getLuminanace(colorA);
#   const lumB = getLuminanace(colorB);
#
#   return (Math.max(lumA, lumB) + 0.05) / (Math.min(lumA, lumB) + 0.05);
# };
#
# // usage:
# const back_color = [255,255,255]; //white
# const text_color = [255,255,0]; //yellow
#
# getContrastRatio(back_color, text_color); // 1.0736196319018405
#
#

    @staticmethod
    def generateFontPreview(font):
        new_image = Image.new('RGB', (100, 40))
        new_image_draw_context = ImageDraw.Draw(new_image)
        new_image_draw_context.rectangle((0, 0, new_image.width, new_image.height),
                                         fill=(255, 255, 255))
        new_image_draw_context.text((int(new_image.width / 2), int(new_image.height / 2)),
                                    "Example", (0, 0, 0), font=font, anchor="mm")
        return new_image

    @staticmethod
    def pixelate(image, pixel_size, resize_mode):
        a_image = image.resize(
            (image.size[0] // pixel_size, image.size[1] // pixel_size),
            resize_mode
        )
        #a_image = a_image.resize(
        #    (image.size[0] * pixel_size, image.size[1] * pixel_size),
        #    resize_mode
        #)
        return a_image

    def convertImage(self, input_image, quantize_method, color_amount):
        piximg = input_image.quantize(method=quantize_method, dither=0, colors=color_amount, kmeans=1)

        piximg = piximg.convert("RGBA")
        na = np.array(piximg)
        colours, counts = np.unique(na.reshape(-1, 4), axis=0, return_counts=True)

        self.possibleColorValuesForAlpha.clear()
        self.possibleColorValuesForAlpha.append("None")
        for a in colours:
            col_str = "#{:02x}{:02x}{:02x}|{:02x}".format(a[0], a[1], a[2], a[3])
            self.possibleColorValuesForAlpha.append(col_str)
        return piximg

    def  preparePaletteData(self):
        palettedata = [255, 255, 255, 93, 143, 241, 233, 136, 56, 239, 148, 84]
        while len(palettedata) < 768:
            palettedata.append(0)
            palettedata.append(0)
            palettedata.append(0)
        palimage = Image.new('P', (12, 12))
        palimage.putpalette(palettedata)
        return palimage
        # return piximg.quantize(method=param_quantMode.value, colors=u.value, dither=Image.NONE, palette=palimage)
