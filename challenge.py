import csv
import sys
import argparse
import json
import xml.etree.ElementTree as ET

def tsv(input_file):
    results = []
    with open(input_file, 'r', encoding='utf-8') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        next(tsv_reader)
    
        for row in tsv_reader:
            data = {}
            name = ""
            zip_code = row[8]
            if row[0] != '':
                name += row[0] + ' '
            if row[1] != 'N/M/N' and row[1] != '':
                name += row[1] + ' '
            if row[2] != '':
                name += row[2]
            if name:
                data['name'] = name
            if row[3] != 'N/A':
                data['organization'] = row[3]
            data['street'] = row[4]
            data['city'] = row[5]
            if row[7] != '':
                data['county'] = row[7]    
            data['state'] = row[6]
            if row[9]:
                zip_code += '-' + row[9]
            data['zip'] = zip_code
                
            results.append(data)
                
        return results

def xml(input_file):
    results = []
    tree = ET.parse(input_file)
    root = tree.getroot()
    for entity in root.findall('ENTITY/ENT'):
        data = {}
        print("strip==", entity.find('NAME').text.strip())
        if entity.find('NAME').text.strip() != '':
            data['name'] = entity.find('NAME').text.strip()
        if entity.find('COMPANY').text.strip() != '':
            data['company'] = entity.find('COMPANY').text.strip()
            
        data['street'] = entity.find('STREET').text
        data['city'] = entity.find('CITY').text
        data['state'] = entity.find('STATE').text
        
        if entity.find('COUNTRY').text.strip() != '':
            data['country'] = entity.find('COUNTRY').text.strip()
        if entity.find('NAME').text.strip() != '-':
            data['zip'] = entity.find('POSTAL_CODE').text.strip()[:-2].replace(' - ', '-')
            
        results.append(data)
        
    return results
        
def txt(input_file):
    with open(input_file, 'r') as file:
        results = []
        lines = file.readlines()
        # 끝에는 개행 문자가 포함되어있음 그래서 한칸 띄게 됨
        necessary_info = []
        data = {}
        for line in lines[2:]: 
            zip_index = 1
            # 중간에 빈 문자 라인 만나면
            if line.strip() == '':
                data['name'] = necessary_info[0].strip()
                data['street'] = necessary_info[1].strip()
                # 라인이 4개일때
                if len(necessary_info) == 4:
                    county = necessary_info[2].strip().split(' ')
                    
                    data['county'] = county[0]
                city_state_zip = necessary_info[len(necessary_info) - 1].strip().split(', ')            
                data['city'] = city_state_zip[0]
                state_zip = city_state_zip[1].split()
                if len(state_zip) > 2:
                    print("state 0 ==",state_zip[0])
                    print("state 1 ==",state_zip[1])
                    data['state'] = state_zip[0].strip() + ' ' + state_zip[1].strip()  
                    print("==data: ", data['state'])
                    
                    zip_index = 2                      
                else:
                    data['state'] = state_zip[0]
                
                if state_zip[zip_index][-1] == '-':
                    data['zip'] = state_zip[zip_index][:-1]  # '-'를 제외한 문자열을 사용
                else:
                    data['zip'] = state_zip[zip_index]
                    
                results.append(data)
                data = {}
                necessary_info = []
                continue
            necessary_info.append(line)
        
        return results
                
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process input files and output a list of addresses.")
    parser.add_argument("input_file", help="Path to the input TSV file")
    return parser.parse_args()

def check_arguments(args):
    if not args.input_file:
        print("Error: Input file path is missing.", file=sys.stderr)
        sys.exit(1)

def check_input_file(input_file, file_extension):
    try:
        if file_extension == 'tsv':
            return tsv(input_file)
        elif file_extension == 'xml':
            return xml(input_file)
        elif file_extension == 'txt':
            return txt(input_file)
        else:
            print(f"Error: Unsupported file type {file_extension} ", file=sys.stderr)
            sys.exit(1)
                    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except csv.Error:
        print(f"Error: Invalid format in input file '{input_file}'.", file=sys.stderr)
        sys.exit(1)

def main():
    args = parse_arguments()
    check_arguments(args)
    file_path = args.input_file
    file_extension = file_path.split('.')[-1]
    json_data = check_input_file(args.input_file, file_extension)
    sorted_json_data = sorted(json_data, key=lambda x: x.get('zip', ''))
    print(sorted_json_data)
    #with open("output.json", 'w', encoding='utf-8') as json_file:
    #    json.dump(sorted_json_data, json_file, indent=4)
    sys.exit(0)

if __name__ == "__main__":
    main()