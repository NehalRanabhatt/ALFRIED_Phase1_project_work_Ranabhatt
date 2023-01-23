library(shiny)
library(shinyTime)
library(plyr)

ui <- shinyUI(pageWithSidebar(
  
  headerPanel("Milkrun cycles in a day"),
  sidebarPanel(
    tabsetPanel(
      tabPanel("Boundary conditions",
               timeInput("starting_time", "Starting time", value = strptime("05:00:00", "%T")),
               timeInput("second_shift", "Second shift starts", value = strptime("14:00:00", "%T")),
               timeInput("third_shift", "Third shift starts", value = strptime("18:30:00", "%T")),
               timeInput("end_time", "End time", value = strptime("03:00:00", "%T")),
               sliderInput("order_delivery_time_difference", "Difference between order and latest delivery times of the containers (minutes):",min = 200, max = 300, value = c(240,260)),
               sliderInput("parkingP2_to_assemblyHall", "Time to reach at assembly hall from p2 parking : arrival_time_p2 and at_assembly_hall (minutes):",min = 20, max = 60, value = c(30,40)),
               sliderInput("assemblyHall_to_assemblyBelt", "Time to reach assembly belt from assembly hall:waiting_time_at_assembly	 (minutes):",min = 10, max = 60, value = c(20,30))
      ),
      tabPanel("Variable-settings",
               numericInput('swapbody_time', 'Enter swapbody time(minutes):',30),##make this variable range
               numericInput('unloading_time_per_container_p2', 'Enter unloading time per container(minutes):',2,min=1,max=4),
               numericInput('loading_time_per_container_p2', 'Enter loading time per container(minutes):',2,min=1,max=4),
               sliderInput("unloading_container_num_range", "Select number of unloaded containers at plant2:",min = 0, max = 30, value = c(12,20)),
               sliderInput("loading_container_num_range", "Select number of loaded containers at plant2:",min = 0, max = 30, value = c(0,8)),
               sliderInput("oneway_trip_time_range", "Enter trip time one way(minutes):",min = 5, max = 30, value = c(5,8)),
               timeInput("first_break_start", "First break starts", value = strptime("09:15:00", "%T")),
               timeInput("second_break_start", "Second break starts", value = strptime("10:20:00", "%T")),
               selectInput("first_break_duration", 
                           label = "Select first break duration",
                           choices = c(15,
                                       20,
                                       25, 
                                       30,
                                       60,
                                       120),
                           selected = 15),
               selectInput("second_break_duration", 
                           label = "Select second break duration",
                           choices = c(15, 
                                       20,
                                       25, 
                                       30,
                                       60,
                                       120),
                           selected = 20)
      )
    )
  ),
  
  
  mainPanel(
    tableOutput("text_o")
  )
)
)

server <- function(input, output) {
  
  
  selected_unloaded_container_vec <- reactive({
    c(input$unloading_container_num_range[1],input$unloading_container_num_range[2])
  })
  selected_loaded_container_vec <- reactive({
    c(input$loading_container_num_range[1],input$loading_container_num_range[2])
  })
  selected_trip_time_vec <- reactive({
    c(input$oneway_trip_time_range[1],input$oneway_trip_time_range[2])
  })
  selected_break_duration_vec <- reactive({
    c(strtoi(input$first_break_duration),strtoi(input$second_break_duration))
  })
  first_break_date_time_combined <- reactive({
    paste("2021/08/01",strftime(input$first_break_start, format="%H:%M:%S"))
  })
  second_break_date_time_combined <- reactive({
    paste("2021/08/01",strftime(input$second_break_start, format="%H:%M:%S"))
  })
  
  output$text_o <- renderTable({
    global_cycleRuns_list <- list()##this is the list for table 1
    first_table_header=c("cycleRuns","comments",
                         "arrival_time_p1",
                         "no. of cont. ordered(=no.of cont.load p1/no.of cont.unload p2)",
                         "depart_time_p1",
                         "trip_time_p1_p2",
                         "comments",
                         "arrival_time_p2",
                         "no. of cont. loaded",
                         "depart_time_p2",
                         "trip_time_p2_p1",
                         "cycle_time")
    global_cycleRuns_list[[1]]=first_table_header
    starting_time=as.POSIXct("2021/08/01 05:00:00")
    container_count=1
    end_time=as.POSIXct("2021/08/02 03:00:00")
    previous_end_time=as.POSIXct("2021/08/01 03:30:00") ##purpose to generate order time
    container_records=list() ##this is the list for table 2
    container_records_header=c("no. of containers",
                               "order_time",
                               "left_time_p1",
                               "arrival_time_p2",
                               "at_assembly_hall",
                               "waiting_time_at_assembly",
                               "actual_assembly_belt_time",
                               "latest_assembly_belt_time",
                               "replishment_status")
    container_records[[1]]=c(container_records_header)
    min=60
    trip_num=0
    first_break_start=as.POSIXct(first_break_date_time_combined()) 
    second_break_start=as.POSIXct(second_break_date_time_combined()) 
    break_time=c(first_break_start,second_break_start)
    break_duration=c(selected_break_duration_vec()[1]*min,selected_break_duration_vec()[2]*min)#converted in to seconds
    swapBody_time=input$swapbody_time*min
    
    while (starting_time+70*60<end_time){
      cycleRuns_record <- c() ##collect the record for the table 1
      ###################plant1###########################################################################################
      milk_run_time=0 ## this is the cycle time
      trip_num=trip_num+1
      unloadNumber_containers_p2=sample(selected_unloaded_container_vec()[1]:selected_unloaded_container_vec()[2],1)
      time_difference=as.numeric(starting_time-previous_end_time)*min*min ## as.numeric gives output in hours, convert in sec.
      order_time=previous_end_time+sort(sample(1:time_difference,unloadNumber_containers_p2))
      #print(order_time)
      previous_end_time=starting_time
      time_intervals_delivery=sample(14400:15600,unloadNumber_containers_p2) ##for every container this will generate random time interval (240-260 mins) between order and delivery time (in mins.)
      delivery_time=order_time+time_intervals_delivery
      left_time_p1=starting_time+swapBody_time
      milk_run_time=milk_run_time+swapBody_time
      trip_time_oneWay=sample(selected_trip_time_vec()[1]:selected_trip_time_vec()[2],1)*min
      
      ## break time logic 
      old_left_time_p1=left_time_p1
      for(i in 1:length(break_time)){
        if((break_time[i]>=starting_time && break_time[i]<=left_time_p1) || 
           (break_time[i]>=left_time_p1 && break_time[i]<=left_time_p1+trip_time_oneWay)){
          left_time_p1=left_time_p1+break_duration[i]
          milk_run_time=milk_run_time+break_duration[i]
        }
      }
      cycleRuns_record <- c(cycleRuns_record,trip_num) ##trip number is cycle run
      
      if(old_left_time_p1 !=left_time_p1){
        cycleRuns_record <-c(cycleRuns_record,"break")
        ###here we have a break
        cat(sprintf("%d\t  %s\t %s\t  %d\t %d\t %s\t",
                    trip_num,starting_time,"break",unloadNumber_containers_p2,(trip_time_oneWay/60),left_time_p1))
      }
      else{
        cycleRuns_record <- c(cycleRuns_record,"-")
        cat(sprintf("%d\t  %s\t %s\t %d\t %d\t %s\t",trip_num,starting_time,"none",unloadNumber_containers_p2,(trip_time_oneWay/60),left_time_p1))
      }
      cycleRuns_record <- c(cycleRuns_record,
                            format(as.POSIXct(starting_time), format = "%H:%M:%S"),
                            unloadNumber_containers_p2,
                            format(as.POSIXct(left_time_p1), format = "%H:%M:%S"),
                            (trip_time_oneWay/60)
                            )
      truck_depart_time_p1=rep(left_time_p1,each=unloadNumber_containers_p2) ## vector of depart time with length equal to num containers
      ###################plant2##############
      milk_run_time=milk_run_time+trip_time_oneWay
      starting_time=left_time_p1+trip_time_oneWay ##arrival at plant 2
      
      left_time_p2=starting_time+unloadNumber_containers_p2*input$unloading_time_per_container_p2*min
      
      loadNumber_containers_p2=sample(selected_loaded_container_vec()[1]:selected_loaded_container_vec()[2],1)
      left_time_p2=left_time_p2+loadNumber_containers_p2*input$loading_time_per_container_p2*min
      ##break logic
      old_left_time_p2=left_time_p2
      trip_time_oneWay=sample(selected_trip_time_vec()[1]:selected_trip_time_vec()[2],1)*min
      milk_run_time=milk_run_time+unloadNumber_containers_p2*input$unloading_time_per_container_p2*min
      milk_run_time=milk_run_time+loadNumber_containers_p2*input$loading_time_per_container_p2*min
      for(i in 1:length(break_time)){
        if((break_time[i]>=starting_time && break_time[i]<=left_time_p2) || 
           (break_time[i]>=left_time_p2 && break_time[i]<=left_time_p2+trip_time_oneWay)){
          left_time_p2=left_time_p2+break_duration[i]
          milk_run_time=milk_run_time+break_duration[i]
        }
      }
      if(old_left_time_p2 !=left_time_p2){
        
        cycleRuns_record <-c(cycleRuns_record,"break")
        ###here we have a break
        cat(sprintf("%d\t  %s\t %s\t  %d\t %d\t %s\n",trip_num,starting_time,"break",loadNumber_containers_p2,(trip_time_oneWay/60),left_time_p2))
      }
      else{
        cycleRuns_record <-c(cycleRuns_record,"-")
        cat(sprintf("%d\t  %s\t %s\t %d\t %d\t %s\n",trip_num,starting_time,"none",loadNumber_containers_p2,(trip_time_oneWay/60),left_time_p2))
      }
      cycleRuns_record <- c(cycleRuns_record,
                            format(as.POSIXct(starting_time), format = "%H:%M:%S"),
                            loadNumber_containers_p2,
                            format(as.POSIXct(left_time_p2), format = "%H:%M:%S"),
                            (trip_time_oneWay/60),
                            (milk_run_time+trip_time_oneWay)/60
      )
      ##now append the cycle record to print the second table
      #print(length(cycleRuns_record))
      global_cycleRuns_list[[length(global_cycleRuns_list)+1]] <- cycleRuns_record
      #observe(global$lst)
      arrival_time_all_containers_p2=rep(starting_time,each=unloadNumber_containers_p2)
      
      time_intervals_assembly_hall=sample(1800:2400,unloadNumber_containers_p2) # time to reach assembly hall from p2-parking (30-40 minutes)
      
      arrival_time_assembly_hall=arrival_time_all_containers_p2+time_intervals_assembly_hall 
      
      time_intervals_belt=sample(1200:1800,unloadNumber_containers_p2) # time to assembly belt from assembly hall (20-30 minutes)
      
      arrival_time_belt=arrival_time_assembly_hall+time_intervals_belt
      
      for (rec in 1:length(order_time)){
        #tmpVec=c(order_time[rec],truck_depart_time_p1[rec],arrival_time_all_containers_p2[rec],
        #arrival_time_assembly_hall[rec],arrival_time_belt[rec],delivery_time[rec])
        #tmpVec=as.POSIXct(tmpVec,origin="1970-01-01")
        status="fail"
        if(arrival_time_belt[rec]<delivery_time[rec]){status="pass"}
        tmpVec=c(container_count,
                 format(as.POSIXct(order_time[rec]), format = "%H:%M:%S"),
                 format(as.POSIXct(truck_depart_time_p1[rec]), format = "%H:%M:%S"),
                 format(as.POSIXct(arrival_time_all_containers_p2[rec]), format = "%H:%M:%S"),
                 format(as.POSIXct(arrival_time_assembly_hall[rec]), format = "%H:%M:%S"),
                 round(time_intervals_belt[rec]/min,3),
                 format(as.POSIXct(arrival_time_belt[rec]), format = "%H:%M:%S"),
                 format(as.POSIXct(delivery_time[rec]), format = "%H:%M:%S"),
                 status
        )
        container_records[[length(container_records)+1]]=tmpVec
        #print(container_records)
        container_count=container_count+1
      }
      #print(global$lst)
      starting_time=left_time_p2+trip_time_oneWay
      
    }##end whileloop
    #container_records1=do.call(c, list(global_cycleRuns_list, container_records))
    blankList=list()
    for (countspace in 1:3){
      blankVec=rep(" ",each=12)
      blankList[[length(blankList)+1]]=blankVec
    }
    df1=data.frame(matrix(unlist(global_cycleRuns_list), nrow=length(global_cycleRuns_list), byrow=TRUE))#table1
    df3=data.frame(matrix(unlist(container_records), nrow=length(container_records), byrow=TRUE))#table2
    df2=data.frame(matrix(unlist(blankList), nrow=length(blankList), byrow=TRUE))
    rbind.fill(df1,df2,df3)
  })
  
  #output$tmp_table <- renderTable({
  #  data.frame(matrix(unlist(global$lst), nrow=length(global$lst), byrow=TRUE))
    #tmp_vec[1]
  #})
  
}
shinyApp(ui, server)