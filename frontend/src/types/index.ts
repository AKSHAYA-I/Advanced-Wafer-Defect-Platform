export type Wafer={temperature_c:number;pressure_torr:number;gas_flow_sccm:number;etch_rate_nm_min:number;voltage_v:number;current_ma:number;process_step:string};
export const initialWafer:Wafer={temperature_c:450,pressure_torr:35,gas_flow_sccm:150,etch_rate_nm_min:80,voltage_v:220,current_ma:15,process_step:'Etching'};
