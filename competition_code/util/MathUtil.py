class MathUtil:

    @staticmethod
    def input_modulus(input, min_input, max_input):
        modulus = max_input - min_input

        num_max = int((input-min_input)/modulus)

        input -= num_max * modulus

        num_min = int((input-max_input)/modulus)
        input -= num_min * modulus

        return input

