use std::env;
use std::fs;
use std::iter::{Map, Filter};
use std::str::SplitWhitespace;
use std::cmp;

// // fn parse(input: String) -> Vec<i32> {
// //     input
// //         .split_whitespace()
// //         .filter(|x| !x.is_empty())
// //         .map(|x| x.parse::<i32>().unwrap())
// //         .collect()
// // }

// // fn parse<'a>(input: String) -> Map<Filter<'a SplitWhitespace, String>, i32> {
// // fn parse(input: String) -> impl Iterator<Item = i32> {
// //     input
// //         .split_whitespace()
// //         .filter(|x| !x.is_empty())
// //         .map(|x| x.parse::<i32>().unwrap())
// // }

// fn parse_split<'a>(input: &str) -> SplitWhitespace {
//     input.split_whitespace()
// }

fn parse_split(input: &str) -> SplitWhitespace {
    input.split_whitespace()
}

fn parse_into_ints(strings: SplitWhitespace) -> Vec<i32> {
    strings.filter(|x| !x.is_empty())
        .map(|x| x.parse::<i32>().unwrap()).collect()
}

// fn parse_into_ints_iter<'a>(strings: SplitWhitespace) -> std::iter::Map<std::iter::Filter<std::str::SplitWhitespace<'_>, Fn(String) -> String>, Fn(String) -> i32> {
//     strings.filter(|x| !x.is_empty())
//         .map(|x| x.parse::<i32>().unwrap())
// }

fn parse_into_ints_iter<'a, F1, F2>(strings: &'a mut SplitWhitespace) -> Map<Filter<SplitWhitespace<'a>, F1>, F2> 
where
    F1: FnMut(&&String) -> bool,
    F2: FnMut(&&String) -> i32,
{
    strings.filter::<F1>(|x| !x.is_empty())
        .map::<F2>(|x| x.parse::<i32>().unwrap())
}

// [closure@src/main.rs:37:20: 37:37]>, [closure@src/main.rs:38:14: 38:43]

fn parse(input: String) -> Vec<i32> {
    let string_split = parse_split(&input);
    parse_into_ints(string_split)
}

fn parse_iter(input: String) {
    let string_split = parse_split(&input);
    parse_into_ints_iter(string_split)
    // string_split.filter(|x| !x.is_empty())
    //     .map(|x| x.parse::<i32>().unwrap())
    //     .collect()
}

// // fn parse_into_ints<T: ?Sized>(iter: &Iterator<Item = T>) -> Vec<i32> {
// //     iter.filter(|x| !x.is_empty())
// //         .map(|x| x.parse::<i32>().unwrap())
// // }

// // fn parse_into_ints(strings: Vec<String>) -> Vec<i32> {
// fn parse_into_ints(strings: &SplitWhitespace) -> Vec<i32> {
//     strings.filter(|x| !x.is_empty())
//         .map(|x| x.parse::<i32>().unwrap()).collect()
// }

// fn parse(input: String) -> Vec<i32> {
//     // let string_split = parse_split(&input).collect();
//     let string_split = parse_split(&input);
//     let int_iter = parse_into_ints(&string_split);
//     // int_iter.collect()
//     int_iter
// }

fn get_solution(input: &String) -> i32 {
    input
        .split_whitespace()
        .filter(|x| !x.is_empty())
        .map(|x| x.parse::<i32>().unwrap())
        .map(fuel_req)
        .sum()
}

fn get_solution2(input: &String) -> i32 {
    input
        .split_whitespace()
        .filter(|x| !x.is_empty())
        .map(|x| x.parse::<i32>().unwrap())
        .map(fuel_fuel)
        .sum()
}

fn fuel_req(mass: i32) -> i32 {
    mass / 3 - 2
}

fn fuel_fuel(mass: i32) -> i32 {
    let req = fuel_req(mass);
    if req > 0 {
        req + fuel_fuel(req)
    } else {
        cmp::max(0, req)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_12() {
        assert_eq!(fuel_req(12), 2);
    }

    #[test]
    fn test_14() {
        assert_eq!(fuel_req(14), 2);
    }

    #[test]
    fn test_1969() {
        assert_eq!(fuel_req(1969), 654);
    }

    #[test]
    fn test_100756() {
        assert_eq!(fuel_req(100756), 33583);
    }

    #[test]
    fn test_parsing() {
        let test_val = "12\n14\n1969\n100756".to_string();
        assert_eq!(
            get_solution(&test_val),
            34241
        );
    }

    #[test]
    fn test_parsing_extra_line() {
        let test_val = "12\n14\n1969\n100756\n".to_string();
        assert_eq!(
            get_solution(&test_val),
            34241
        );
    }

    #[test]
    fn test_fuel_fuel_14() {
        assert_eq!(fuel_fuel(14), 2);
    }

    #[test]
    fn test_fuel_fuel_1969() {
        assert_eq!(fuel_fuel(1969), 966);
    }

    #[test]
    fn test_fuel_fuel_100756() {
        assert_eq!(fuel_fuel(100756), 50346);
    }
}

fn main() {
    // Load data
    let args: Vec<String> = env::args().collect();
    let filename = &args[1];

    let contents = fs::read_to_string(filename)
        .expect("Something went wrong reading the file");
    
    // Get results
    let result = get_solution(&contents);
    let result2 = get_solution2(&contents);

    // Print results
    println!("Result: {:}", result);
    println!("Result2: {:}", result2);
}
