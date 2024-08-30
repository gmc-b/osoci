import os
from os.path import dirname, abspath
import opensim as osim
import os
import json
import numpy as np
import time




def setup(setup_file):
    with open(setup_file) as json_file:
        file_contents = json_file.read()
        setup_dic = json.loads(file_contents)
    return setup_dic

def analyse_tool_setup(model,model_full_path,movement_full_path,output_full_path,start_time,final_time,step_interval):
    analyze_tool = osim.AnalyzeTool()
    analyze_tool.setName("analyze")
    analyze_tool.setModelFilename(model_full_path)
    analyze_tool.setModel(model)
    analyze_tool.setCoordinatesFileName(movement_full_path)
    analyze_tool.setStartTime(start_time)
    analyze_tool.setFinalTime(final_time) 
    analyze_tool.setLoadModelAndInput(True)
    analyze_tool.setResultsDir(output_full_path)

    return analyze_tool


def get_time_parameters(motion): 
    step_interval = motion.getStepInterval()
    start_time    = motion.getFirstTime()
    final_time    = motion.getLastTime()

    return [start_time,final_time,step_interval]

def body_kinematic_analysis(model,start_time,final_time,step_interval):
    body_kinematics = osim.BodyKinematics()
    body_kinematics.setModel(model)
    body_kinematics.setStartTime(start_time)
    body_kinematics.setEndTime(final_time) 
    body_kinematics.setStepInterval(step_interval) 
    body_kinematics.setInDegrees(True)  
    body_kinematics.setRecordCenterOfMass(True)

    return body_kinematics

def format_numpy_array (data, column_name,time=False):

    column_data = osim.ArrayDouble()

    if (time):
        data.getTimeColumn(column_data)
    else:
        data.getDataColumn(column_name, column_data)

    np_data = np.array([column_data.get(i) for i in range(column_data.getSize())])

    return np_data





def detect_jump(data, stability_time = 1, sample_rate = 60):

    stability_window = stability_time*sample_rate   # janela de frames para se analisar estabildiade
    
    max_height_index = data.argmax()
    analisys_start_index = max_height_index - stability_window

    
    threshold = 0
    jump_start_index = max_height_index
    baseline_data  = data[analisys_start_index:jump_start_index] 

    while(baseline_data[-1] > threshold):
        baseline_data  = data[analisys_start_index:jump_start_index] 
        base_line_mean = baseline_data.mean()
        baseline_std   = np.std(baseline_data)
        threshold      = base_line_mean + 2 * baseline_std  # Regra empírica do desvio padrão
        jump_start_index -= 1

    return jump_start_index, max_height_index



def post_procces_body_kinematics(output_full_path):
    
    folder    = output_full_path.split("\\")[-3]
    file_name = output_full_path.split("\\")[-1]

    pos_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_pos_global.sto" )
    vel_file_path = os.path.join(output_full_path,"analyze_BodyKinematics_vel_global.sto" )
    
    pos_data      = osim.Storage(pos_file_path)
    vel_data      = osim.Storage(vel_file_path)

    output_string = "               [{folder}][{file_name}]\n\n".format(folder = folder, file_name = file_name) 

    time_column = format_numpy_array(pos_data, "", time=True)
    cmy_column  = format_numpy_array(pos_data, "center_of_mass_Y")


    # Análise de altura máxima
    max_height       = cmy_column.max()
    max_height_index = cmy_column.argmax()
    max_height_time  = time_column[max_height_index]


    output_string += "Altura CM[Máxima]: {max_height}m ({max_height_time}s)\n\n".format(max_height = max_height,max_height_time=max_height_time) 
    
######################################################################################################

    
    tyr_pos_column = format_numpy_array(pos_data, "toes_r_Y")
    #tyl_pos_column = format_numpy_array(pos_data, "toes_l_Y")
    #tymean_pos_column = (tyr_pos_column + tyl_pos_column) /2

    jump_start_index, max_height_index = detect_jump(tyr_pos_column)

    output_string += "Altura halúx[início de salto]:{height_start:4f} ({time_start})s \n".format(height_start = tyr_pos_column[jump_start_index],time_start = time_column[jump_start_index]) 
    output_string += "Altura halúx[final de salto ]:{height_final:4f} ({time_final})s \n\n".format(height_final = tyr_pos_column[max_height_index],time_final = time_column[max_height_index]) 
######################################################################################################

    tyr_vel_column = format_numpy_array(vel_data, "toes_r_Y")
    #tyl_vel_column = format_numpy_array(vel_data, "toes_l_Y")

    #tymean_vel_column = (tyr_vel_column + tyl_vel_column) /2

    output_string += "Velocidade hálux[início de salto]:\n"

    for i in range(10):
        output_string += "-> {vel:4f} m/s \t({time}s)\n".format(vel = tyr_vel_column[jump_start_index+i],time = time_column[jump_start_index+i]) 

######################################################################################################

    outut_text_file_path = os.path.join(output_full_path, "bk_results.txt") 
    with open(outut_text_file_path, mode="w", encoding='utf-8') as text_output_file:
        text_output_file.write(output_string)
        print(output_string)


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Um erro ocorreu ao tentar deletar o arquivo temporário: {e}")


analysis_function_dic    = {"body_kinematics":body_kinematic_analysis}
pp_analysis_function_dic = {"body_kinematics":post_procces_body_kinematics}


def main():
    start_time = time.time()
    dir_name = dirname(abspath(__file__))
    
    setup_dic           = setup("setup.json")
    tools               = setup_dic["tools"]
    opencap_folder_list = setup_dic["opencap_folder_list"] 
    
    analysis_list       =  tools["analyze"]

    analyize_file_path  = "tmp/analyze_setup.xml"

    data_path           = os.path.join(dir_name,"data")

    for folder in opencap_folder_list:

        opencap_folder_name = folder["folder_name"]
        model_file          = folder["model_file"]
        mot_file_list       = folder["movement_file_list"]       

        model_full_path    = os.path.join(data_path, opencap_folder_name, "OpenSimData", "Model", model_file)
        # Carrega o modelo
        model = osim.Model(model_full_path)        
######################################################################################################################################
        for mot_file_name in mot_file_list:

            mot_file_name_base = os.path.splitext(mot_file_name)[0]
            movement_full_path = os.path.join(data_path, opencap_folder_name, "OpenSimData", "Kinematics", mot_file_name)
            output_full_path   = os.path.join(data_path, opencap_folder_name,"output" ,mot_file_name_base)
            os.makedirs(output_full_path, exist_ok=True) # Necessário pois são criados diretórios intermediários
            motion = osim.Storage(movement_full_path)
            time_parameters = get_time_parameters(motion)

            # Configura a ferramenta Analyze
            analyze_tool = analyse_tool_setup(model,model_full_path,movement_full_path,output_full_path,*time_parameters)

            for analysis in analysis_list:
                try:
                    analyze_function = analysis_function_dic[analysis]

                except Exception as e:
                    print(f"Erro ao reconhecer a análise {analysis}, verifique a ortografia e o suporte à análise requerida na documentação")
                    print(f"Erro: {e}")
                    return
                
                analysis_config = analyze_function(model,*time_parameters)    # adicionar **kwargs para generalização de parâmetros, se necessário
                analyze_tool.updAnalysisSet().cloneAndAppend(analysis_config)


            analyze_tool.printToXML(analyize_file_path)
######################################################################################################################################
            # Executa a ferramenta Analyze
            try:
                analyze_tool = osim.AnalyzeTool(analyize_file_path)
                analyze_tool.run()
                print("A análise foi executada com sucesso.")
            except Exception as e:
                print(f"Erro ao executar a análise: {e}")
                return
        
        # pós processamento
        for mot_file_name in mot_file_list:
            mot_file_name_base   = os.path.splitext(mot_file_name)[0]
            output_full_path     = os.path.join(data_path, opencap_folder_name, "output",mot_file_name_base)
            for analysis in analysis_list:
                pp_analysis_function_dic[analysis](output_full_path)



    delete_file(analyize_file_path)
    end_time = time.time()
    print("Tempo de execução:",end_time - start_time)

if __name__ == "__main__":
    main()