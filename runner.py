base_path ="C:\ActiveTcl\Loop\wire_0_93nm\\test_oommf\\test_calc"
oommf_path = "C:\ActiveTcl"
import csv
import subprocess
import io
import datetime



def func_for_calculateHcMr(file_name):
    with open(base_path +'\\'+file_name,encoding='utf-8') as csv_results:  
        csv_data_reader = csv.DictReader(csv_results, delimiter = ",")
        # я готова начать читать последовательность символов
        M = ''
        B = ''
        number_B_previous = -1.0
        number_M_previous = -1.0
        Hc = 0.0
        Mr = 0.0
        for data_row in csv_data_reader:
                
                B = data_row['  Oxs_UZeeman::Bz (mT)']
                M = data_row[' Oxs_MinDriver::mz']
                
                #переделаем строки в числа
            
                number_B = float(B)
                number_M = float(M)
                # print (number_B, number_M)
                # Ищеи точку пересечения с у
                if number_B == 0:
                    Mr = number_M
                    print (Mr)
                elif number_B>0 and number_B_previous < 0:
                    Mr = (number_B_previous*number_M-number_M_previous*number_B)/(number_B_previous-number_B)
                    print (Mr)
                
                # Ищем точку пересечения с х
                if number_M == 0:
                    Hc = number_B
                    print (Hc)
                elif number_M>0 and number_M_previous < 0:
                    Hc = (number_B_previous*number_M-number_M_previous*number_B)/(number_M-number_M_previous)
                    print (Hc)    
                
                number_B_previous = number_B
                number_M_previous = number_M
    if Hc < 0: Hc = -Hc
    if Mr < 0: Mr = -Mr
    return (Hc, Mr)
    #делаем процедуру для сохранения всех данных в один файл
def save_file_HcMr_and_const(base_path, array_data):
    #Имя файлп- строка - которая будет названием самого важного файла со всеми констатами и расчетными данными
#создаем (пустой) массив для всех вычисленных Нс и Mr, записывая результат Нс и Mr для каждого набора констант
# имя переменной с названием файла (создаем строку):
    date_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name_all_const_and_HcMr = ('all_const_and_HcMr' + date_string + '.csv')
    with open(base_path + '//' + file_name_all_const_and_HcMr, 'w', encoding='utf-8') as w_file:
        #w-file указывает на положение файла на жестком диске
        # создаем файл для записи (для построения графиков из полученных данных)
        file_writer = csv.writer(w_file, delimiter = ",")
        file_writer.writerow(['Hc', 'Mr', 'A', 'K', 'H', 'Hstep', 'd', 'Ms', 'L'])
        for row in array_data:
            file_writer.writerow([row['Hc'],row['Mr'], row['A'],row['K'], row['H'],row['Hstep'], row['d'],row['Ms'],row['L']])

all_HcMr_for_each_setofconst = []
with open("A,K,Ms,d,L,cell.csv", encoding='utf-8') as r_file:
    # файл откуда читаются входные константы расчета - объявляем переменную, которая 
    #переменная, построчно читает файл, где лежат константы, создана функцией
    file_reader = csv.DictReader(r_file, delimiter = ",")
   # проходим в цикле по массиву который в данном случае заменяется ридером
   # row - переменная цикла, как счетчик, это значение, которя на каждой итерации считана
    for row in file_reader:
     
        #удаляем odt с результатами перед расчетом
        delet_old_data = ('del "' +base_path+'\cylinder_model.odt"')
        print(delet_old_data)
        subprocess.run(delet_old_data, check=False, shell=True)

        parameters_of_task = ('tclsh '+oommf_path+'\oommf.tcl boxsi  -parameters "Aconst '+ row['A']+
            ' Kconst ' + row['K'] + 
            ' Hconst ' + row['H'] +
            ' Hsteps ' + row['Hstep'] +
            ' Msconst ' + row['Ms'] + 
            '" "' +base_path+'\cylinder_model.mif" -outdir "' +base_path+'"')
        print(parameters_of_task)
        subprocess.run(parameters_of_task, check=False, shell=True)

        file_name = ('A_' + row['A'] +
            '_K_' + row['K'] + 
            '_H_' + row['H'] +
            '_Hsteps_' + row['Hstep'] +
            '_Ms_' + row['Ms'] + '.csv')
    #переделываем рассчитанный odt в csv   
       #удаляется файл csv с расчетом перед командой которая его снова сгенерирует
        delete_data_file_csv = ('del "' +base_path + '\\'+ file_name +'"')
        #возьми переменную base_path и file_name и подставь к del
        print( delete_data_file_csv)
        subprocess.run(delete_data_file_csv, check=False, shell=True)
#создаем csv файл из odt файла, выбирая две колонки с помощью модуля oommf - odtcols - c такими именами - файл с данными - файл, имя которого мы создали с помощью констант
# переменная для имени этого файла - file_name - эта переменная нужна чтобы не копировать длинное имя файла
        file_csv_results = ('tclsh '+oommf_path+'\oommf.tcl odtcols -q -t csv col "Oxs_UZeeman::Bz" "Oxs_MinDriver::mz" <"' +base_path+'\cylinder_model.odt" >"' +base_path+'\\'+ file_name +'"')
        print(file_csv_results)
        subprocess.run(file_csv_results, check=False, shell=True)
        
             # вызов функции вместо цикла - создаем переменную HcMr 
             # фукция посчитала и рузультат записала в НсMr
  
        HcMr = func_for_calculateHcMr(file_name)
        #такой тип структуры данных это кортеж:
        row['Hc'] = HcMr[0]
        row['Mr'] = HcMr[1]
        # добавляем все ряды констант входных  и выходных в один  массив
        all_HcMr_for_each_setofconst.append(row)

print(all_HcMr_for_each_setofconst)

save_file_HcMr_and_const(base_path, all_HcMr_for_each_setofconst)               
        