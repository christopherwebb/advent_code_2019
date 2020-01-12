from typing import List
from pydantic import BaseModel


class Layer(BaseModel):
    image: List[List[int]]

    def find_digit_count(self, digit):
        return len([
            x
            for row in self.image
            for x in row
            if x == digit
        ])


class Image(BaseModel):
    layers: List[Layer]
    height: int
    width: int


def parse_image(str_input, height, width):
    raw_input = [x for x in str_input if not x.isspace()]

    layers = []
    layer_size = height * width
    for layer_index in range(int(len(raw_input) / layer_size)):
        layer_raw = raw_input[layer_index * layer_size:(layer_index + 1) * layer_size]

        rows = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(int(layer_raw.pop(0)))

            rows.append(row)

        layers.append(Layer(image=rows))

    return Image(
        layers=layers,
        height=height,
        width=width,
    )

# Layer 1: 123
#          456

# Layer 2: 789
#          012
test_image_data = '123456789012\n'
test_image = parse_image(test_image_data, 2, 3)
assert len(test_image.layers) == 2
assert test_image.layers[0].image[0] == [1, 2, 3]
assert test_image.layers[0].image[1] == [4, 5, 6]
assert test_image.layers[1].image[0] == [7, 8, 9]
assert test_image.layers[1].image[1] == [0, 1, 2]

def find_layer_fewest_zeros(image):
    zero_counts = {
        index: layer.find_digit_count(0)
        for index, layer in enumerate(image.layers)
    }

    _index = -1
    _min = 1000

    for index, count in zero_counts.items():
        if count < _min:
            _index = index
            _min = count

    layer = image.layers[_index]
    # import pdb; pdb.set_trace()
    return layer.find_digit_count(1) * layer.find_digit_count(2)

with open('input.txt') as f:
    image = parse_image(f.read(), 6, 25)

assert len(image.layers) == 100
result = find_layer_fewest_zeros(image)
print('Found layer value: %s' % result)


def generate_image(image):
    layered = []
    for y in range(image.height):
        layer_row = []

        for x in range(image.width):
            layer_row.append([
                layer.image[y][x] for layer in image.layers
            ])

        layered.append(layer_row)

    # import pdb; pdb.set_trace()
    return FinalImage(image=[
        [
            [p for p in pixel if p != 2][0]
            for pixel in row
        ]
        for row in layered
    ])


class FinalImage(BaseModel):
    image: List[List[int]]

    def create_ppm(self, output_file):
        with open(output_file, 'w') as f:
            f.write('P1\n')
            f.write('%d %d\n' % (
                len(self.image[0]),
                len(self.image),
            ))

            for row in self.image:
                f.write('%s\n' % 
                    ' '.join(str(x) for x in row)
                )


test_image_2_data = '0222112222120000\n'
test_image_2 = parse_image(test_image_2_data, 2, 2)
test_final_image = generate_image(test_image_2)

assert test_final_image.image[0] == [0, 1]
assert test_final_image.image[1] == [1, 0]

test_final_image.create_ppm('test_final_image.pbm')
final_image = generate_image(image)
final_image.create_ppm('output.pbm')









