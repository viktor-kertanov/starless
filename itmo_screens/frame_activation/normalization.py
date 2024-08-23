import numpy as np
import matplotlib.pyplot as plt

def func_normalization(
    target_val,
    min_in,
    max_in,
    min_out,
    max_out,
    func=np.log,
    plot=False):

    x = np.linspace(min_in, max_in, 1000)
    y = func(x)

    y_norm = ((y - np.min(y)) / (np.max(y) - np.min(y))) * (max_out - min_out) + min_out
    y_target = ((func(target_val) - np.min(y)) / (np.max(y) - np.min(y))) * (max_out - min_out) + min_out

    if not plot:
        return y_target
    
    plt.grid()
    plt.title(f"Target: {target_val}. Result: {y_target:.3f}. Function: {func}")
    plt.plot(x, y_norm)
    plt.plot(target_val, y_target, 'ro')
    plt.plot(np.linspace(min_in, target_val, 100), np.ones(100)*y_target, '--', color='red')
    plt.plot(np.ones(100)*target_val, np.linspace(min_out, y_target, 100), '--', color='red')
    plt.plot([min_in, max_in], [min_out, min_out], 'k-')
    plt.plot([min_in, min_in], [min_out, max_out], 'k-')
    plt.axis('on')
    plt.gcf().set_size_inches(10, 10)
    plt.xlim([min_in, max_in])
    plt.ylim([min_out, max_out])
    plt.show()


def func_normalization_int_array(
    min_in,
    max_in,
    min_out,
    max_out,
    func=np.log):
    '''No target value. If we have integers as inputs that are distributed from min to max, we output the 
    array with new, normalized outputs for each value in the range max-min input.
    '''

    x = np.arange(min_in, max_in + 1, dtype=int)
    y = func(x)

    normalized_values = ((y - np.min(y)) / (np.max(y) - np.min(y))) * (max_out - min_out) + min_out

    return normalized_values

def advanced_normalizing_function(
    input: tuple[float, float],
    output: tuple[float, float],
    function_range: tuple[float, float],
    function,
    num_points: int=10000,
    do_plot: bool=False,
):
    '''Advanced normalization, when we normalize over x and y. We can normalize data along the '''
    
    if input[0] >= input[1]:
        raise ValueError(f"Input is wrong, first val must be min, second -- max")
    if output[0] >= output[1]:
        raise ValueError(f"Output is wrong, first val must be min, second -- max")
    if function_range[0] >= function_range[1]:
        raise ValueError(f"Func range is wrong, first val must be min, second -- max")
    
    x_func = np.linspace(np.min(function_range), np.max(function_range), num_points)
    y_func = function(x_func)

    y_func_range = np.max(y_func) - np.min(y_func)
    output_range = np.max(output) - np.min(output)
    y_extend_factor = output_range / y_func_range
    y_func_extended = (y_func - np.min(y_func)) * y_extend_factor + np.min(output)

    x_func_range = np.max(x_func) - np.min(x_func)
    input_range = np.max(input) - np.min(input)
    x_extend_factor = input_range / x_func_range
    x_func_extended = (x_func - np.min(x_func)) * x_extend_factor + np.min(input)

    points = list(zip(x_func_extended, y_func_extended))

    if not do_plot:
        return points
    
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches((6, 6))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    ax[0].plot(x_func, y_func, 'r-')
    ax[0].set_title('Function, curve shape')
    ax[0].axis('on')
    ax[0].grid(True)
    ax[0].set_xlim(function_range[0], function_range[1])
    ax[0].set_ylim(np.min(y_func), np.max(y_func))
    

    ax[1].plot(x_func_extended, y_func_extended, 'g-')
    ax[1].set_title('Normalized function')
    ax[1].axis('on')
    ax[1].grid(True)
    ax[1].set_xlim(np.min(x_func_extended), np.max(x_func_extended))
    ax[1].set_ylim(np.min(y_func_extended), np.max(y_func_extended))
    ax[1].set_yticks(np.arange(0, 125, 5))

    plt.show()

    return points