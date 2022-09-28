---
title: Network Plot
author: yuki
date: '2022-09-28'
slug: network-plot
categories:
  - R
tags:
  - plot
  - code
subtitle: ''
summary: ''
authors: []
lastmod: '2022-09-28T14:34:41+08:00'
featured: no
draft: no
image:
  caption: ''
  focal_point: ''
  preview_only: no
projects: []
summary: the code of network plot
---

```{r}
library("qgraph")
library('ggplot2')
library("bootnet") 
library("dplyr")


setwd("C:/Users/hmz19/Desktop/Mental Health/Network Plot/R_code")
#import data
net_prac<- bruceR::import("C:\\Users\\hmz19\\Desktop\\Mental Health\\Network Plot\\R_code\\dat_cfa_p.csv") %>%
  dplyr::select(.,TAS:HL) %>%
  dplyr::mutate(I=(I1+I2+I3+I4)/4,V=(V1+V2+V3)/3,Kp=Keep,Rl=Release,H_L=HL) %>%
  dplyr::select(.,I,V,Erp,Frp,HSrp,Rrp,Srp,Eeb,Feb,HSeb,Reb,Seb,Kp,Rl,H_L) %>%
  round(.,3) %>%  #decimal=3
  na.omit(.)  #delete missing data

GGM <- estimateNetwork(net_prac, default="EBICglasso") 

#get named correlation matrix (EBICglasso)
get_matrix <- function(raw_matrix){
  named_matrix <- matrix(raw_matrix,nrow=15,ncol=15)
  rownames(named_matrix) <- c("I","V","Erp","Frp","HSrp","Rrp","Srp","Eeb","Feb","HSeb","Reb","Seb","Kp","Rl","H_L")
  colnames(named_matrix) <- c("I","V","Erp","Frp","HSrp","Rrp","Srp","Eeb","Feb","HSeb","Reb","Seb","Kp","Rl","H_L")
return(named_matrix)
}

df <- get_matrix(raw_matrix = GGM$graph)
df
#variables long name
var_name <- c("Impulsive","Venturesome",
              "Ethical Risk Perceptions","Financial Risk Perceptions","Health/Safety Risk Perceptions","Recreational Risk Perceptions","Social Risk Perceptions",
              "Ethical Expected Benefits ","Financial Expected Benefits ","Health/Safety Expected Benefits ","Recreational Expected Benefits ","Social Expected Benefits ",
              "Keep","Release","Holt & Laury")
#create groups
get_group <- function(){
  IV=c(1,2)
  RP=c(3,4,5,6,7)
  EB=c(8,9,10,11,12)
  Y= c(13,14,15)

  names(IV) <- c("I","V")
  names(RP) <- c("Erp","Frp","HSrp","Rrp","Srp")
  names(EB) <- c("Eeb","Feb","HSeb","Reb","Seb")
  names(Y) <- c("Kp","Rl","H_L")

  group=list(IV,RP,EB,Y)
  names(group) <- c("IV","RP","EB","Y")
return(group)
}

risk_group=get_group()
risk_group


library('mgm')
#get pie(residual error)
get_RE <- function(raw_data){
  p <- ncol(raw_data) #number of variables
  
  fit_obj <- mgm(data = raw_data, 
                 type = rep('g', p), #"g" for Gaussian, "p" for Poisson, "c" for categorical.
                 lev = rep(1, p), #continue variable default setting
                 rule.reg = 'OR')
  pred_obj <- predict(fit_obj, raw_data, 
                      error.continuous = 'VarExpl') #fit_obj + data = pred_obj
return(pred_obj$error)
}

RE <- get_RE(raw_data=net_prac)
RE
RE$RMSE

#color
library('viridisLite')
library('viridis')
pal_rb<- viridis(4,option = "H")

#network plot
c1 <- qgraph (df,layout = "groups",groups=risk_group, 
              posCol = "lightgreen", negCol = "pink", #positive & negative line color
              directed = FALSE,esize = 15, #esize: max edge size                
              edge.width = 0.8, edge.labels = F,            
              nodeNames=var_name, #variable names in legend 
              border.color = "grey",border.width = 0.5, #node border color and size
              color = pal_rb, #group color
              label.color = "white", #label color in graph
              pie = RE$RMSE, pieBorder = 0.25, #residual error
              label.cex=2, legend.cex=0.3, GLratio = 1,#graph & legend relative size
              node.width=0.8,node.height=0.8) 


#centrality
c2 <- qgraph::centralityPlot(GGM, 
      include=c("Strength","Betweenness","Closeness","ExpectedInfluence"),
      orderBy = "Strength") 

#centrality stability
c3 <- bootnet(GGM, statistics = c("Strength","Betweenness","Closeness","ExpectedInfluence"), 
              nBoots = 1000, nCores = 16,type = "case") 
plot(c3,statistics = c("Strength","Betweenness","Closeness","ExpectedInfluence")) + 
              theme()

#bootstrap mean
library('relaimpo')
GGM_A <- estimateNetwork(net_prac, default = "relimp",normalize = FALSE, nCores = 16) 
c4 <- bootnet(GGM_A, nBoots = 100, nCores = 16)
plot(c4, plot = "interval", split0 = TRUE, order="sample", labels=FALSE)

#bridge centrality
library('networktools')
c5 <- bridge(c1,communities = c('1','1','2','2','2','2','2','3','3','3','3','3','4','4','4'),
  useCommunities = "all",directed = NULL,
  nodes = NULL,normalize = FALSE)
plot(c5)

#Bootstrapped dierence tests
c6 <- bootnet(GGM, nBoots = 1000, nCores = 16)
plot(c6, "edge", plot = "difference", onlyNonZero = TRUE, order = "sample")
plot(c6,"strength")

#Network comparisons
net_comp<- bruceR::import("C:\\Users\\hmz19\\Desktop\\Mental Health\\Network Plot\\R_code\\dat_cfa_p.csv") %>%
  dplyr::select(.,gender,TAS:HL) %>%
  dplyr::mutate(I=(I1+I2+I3+I4)/4,V=(V1+V2+V3)/3,Kp=Keep,Rl=Release,H_L=HL,
                gender =as.numeric(ifelse(gender=='male',"1","2"))) %>%
  round(.,3) %>%  #decimal=3
  dplyr::select(.,gender,I,V,Erp,Frp,HSrp,Rrp,Srp,Eeb,Feb,HSeb,Reb,Seb,Kp,Rl,H_L) %>%
  na.omit(.)  #delete missing data

#Network centrality comparisons
net_m <- dplyr::filter(net_comp,gender==1) %>%
         dplyr::select(.,-gender) %>%
         estimateNetwork(., default="EBICglasso")
net_f <- dplyr::filter(net_comp,gender==2) %>%
         dplyr::select(.,-gender) %>%
         estimateNetwork(., default="EBICglasso") 

c7 <- qgraph::centralityPlot(list(male=net_m,
                                  female=net_f), 
      include=c("Strength","Betweenness","Closeness","ExpectedInfluence"),
      orderBy = "Strength") 

#Network edge comparisons
#Network plot (draw 2 graph for each group)
library('mgm')
mgm_obj <- mgm(data = net_comp, 
               type = c("c", 
                        "g", "g", 
                        "g", "g", "g","g", "g", 
                        "g", "g", "g","g", "g", 
                        "g", "g", "g"), #variable type c: categorical g: Gaussian(continual)
               level = c(2,
                         1,1,
                         1,1,1,1,1,
                         1,1,1,1,1,
                         1,1,1), #categorical variable level, '1' for continual variables 
               moderators = 1, #row of moderator(categorical variable)
               lambdaSel = "EBIC", 
               lambdaGam = 0.25, 
               ruleReg = "AND", 
               pbar = FALSE)


comp_plot <- function(comp_data,n_group){
  l_mgm_cond <- list()
  for(g in 1:n_group) l_mgm_cond[[g]] <- condition(object = comp_data, #for... fill categorical variable(moderator)'s level
                                           values = list("1" = g)) #list()... fill the row of moderator

  v_max <- rep(NA, n_group)
  for(g in 1:n_group) v_max[g] <- max(l_mgm_cond[[g]]$pairwise$wadj) #the same as above

  par(mfrow=c(1, n_group)) 
  comp_graph <- for(g in 1:n_group) { #categorical variable level (the value must to be same as the raw data)
    qgraph(input = l_mgm_cond[[g]]$pairwise$wadj, 
         edge.color = l_mgm_cond[[g]]$pairwise$edgecolor_cb,
         lty = l_mgm_cond[[g]]$pairwise$edge_lty,
         layout = "circle", mar = c(2, 3, 5, 3),
         maximum = max(v_max), vsize = 5, esize = 10, #vsize = node size; esize = edge size
         edge.labels  = TRUE, edge.label.cex = 3)
    mtext(text = paste0("Group ", g), line = 2.5)
}
return(comp_graph)
}

comp_plot(comp_data = mgm_obj, n_group=2)

#Network moderator effect
res_obj <- mgm::resample(object = mgm_obj, 
                    data = net_comp, 
                    nB = 50, 
                    pbar = FALSE)
plotRes(res_obj)
```  
