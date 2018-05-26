; These files are loaded by default in NCL V6.2.0 and newer
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"

; These files still have to be loaded manually
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRF_contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/time_axis_labels.ncl"

begin
; Make a list of all files we are interested in
  DATADir = "/projects/NS1000K/pernbo/DONE_WRF_EXP/wrfout_d04/"
  FILES = systemfunc (" ls -1 " + DATADir + "wrfout* ")
  a = addfiles(FILES+".nc","r")

;-- Variables to Interpolate
  tc = wrf_user_getvar(a,"tc",-1)        ; T in C
  uvmet  = wrf_user_getvar(a,"uvmet",-1) ; u,v averaged to mass points, and rotated to earth coor
  u = uvmet(0,:,:,:,:)
  v = uvmet(1,:,:,:,:)
;  printVarSummary(u)

;-- Other variables
  T2 = wrf_user_getvar(a,"T2",-1)
  T2  = T2 - 273.15       ; now in celsius
  T2@units = "C"

  uvmet10  = wrf_user_getvar(a,"uvmet10",-1) ; u,v averaged to mass points, and rotated to earth coor @10m
  u10 = uvmet10(0,:,:,:)  
  v10 = uvmet10(1,:,:,:)

;-- Direction and Speed at 10m
  r2d = 45.0/atan(1.0)  ;radians to degrees
  dir10 = atan2(u10,v10) * r2d + 180 ;direction
  spd10 = sqrt(u10^2+v10^2) ;speed

;--Times and time steps
  times = wrf_user_getvar(a,"times",-1)  ; all times in the file
  ntimes = dimsizes(times)         ; number of times in the file

;--The specific height levels that we want the data interpolated to.
  vert_coord       = "ght_agl"
  interp_levels    = (/0.01/)
  nlevels          = dimsizes(interp_levels)  ; number of levels
  interp_levels2   = (/0.0265/)
  nlevels2         = dimsizes(interp_levels2)  ; number of levels
 
  opts             = True
  opts@extrapolate = True 
  opts@field_type  = "T"
  opts@logP        = True 

  opts2             = True
  opts2@extrapolate = True 
  opts2@logP        = True 

;## Interpolation ####################################################   
  tc_interp = wrf_user_vert_interp(a,tc,vert_coord,interp_levels,opts)
  u_interp = wrf_user_vert_interp(a,u,vert_coord,interp_levels2,opts2)
  v_interp = wrf_user_vert_interp(a,v,vert_coord,interp_levels2,opts2)
  ;printVarSummary(u_interp)
;#####################################################################

;-- Direction and Speed at 30m
  dir = atan2(u_interp,v_interp) * r2d + 180 ;direction
  spd = sqrt(u_interp^2+v_interp^2) ;speed

;---Set up TXT file and header information for the file
  txt_filename = "wrf_temp_Blindern.txt"
  system("rm -f " + txt_filename)   ; Remove file in case it exists. 
  format1 = "%s,%s,%g,%g"       ;TIME,GRIDBOX,HEIGHT,TEMP
  header1 = (/"TIME, GRIDBOX, HEIGHT, TEMP"/)
  hlist1 =(/header1/)
  hformat1="%s"

  txt_filename2 = "wrf_wind_Blindern.txt"
  system("rm -f " + txt_filename2)   ; Remove file in case it exists.
  format2 = "%s,%s,%g,%g,%g"           ;TIME,GRIDBOXS,HEIGHT,SPEED,DIR
  header2 = (/"TIME, GRIDBOX, HEIGHT, SPEED, DIR"/)
  hlist2 =(/header2/)
  hformat2="%s"

;-- Locations we want to get data from
  lats = 59.9406   ;Blinder
  lons = 10.7231   ;Blinder
  loc = wrf_user_ll_to_ij(a, lons, lats, True)   ; 2 x nlatnlon
  loc = loc - 1      
  i = loc(0)
  j = loc(1)
  munch =(/i,j/)

;--- Gridboxes around Munch
   g1 = (/i,j+1/) ;North
   g2 = (/i,j-1/) ;South
   g3 = (/i+1,j/) ;East
   g4 = (/i-1,j/) ;West


;-- WRITE TEMP TO FILES
   print("Writing Temperature to file!")
   do it = 0,ntimes-1
     print("Working on time: " + times(it) )  

     ;-- T2 
     list_1 = [/times(it),"blindern","2",T2(it,munch(1),munch(0))/] 
     list_2 = [/times(it),"north","2",T2(it,g1(1),g1(0))/] 
     list_3 = [/times(it),"south","2",T2(it,g2(1),g2(0))/] 
     list_4 = [/times(it),"east","2",T2(it,g3(1),g3(0))/] 
     list_5 = [/times(it),"west","2",T2(it,g4(1),g4(0))/]
     write_table(txt_filename, "a", list_1, "%s,%s,%s,%g")
     write_table(txt_filename, "a", list_2, "%s,%s,%s,%g")
     write_table(txt_filename, "a", list_3, "%s,%s,%s,%g")
     write_table(txt_filename, "a", list_4, "%s,%s,%s,%g")
     write_table(txt_filename, "a", list_5, "%s,%s,%s,%g")

     ;--Interp T
     height = interp_levels(:)*1000
     alist = [/times(it),"blindern",height(0),tc_interp(it,:,munch(1),munch(0))/] 
     blist = [/times(it),"north",height(0),tc_interp(it,:,g1(1),g1(0))/] 
     clist = [/times(it),"south",height(0),tc_interp(it,:,g2(1),g2(0))/] 
     dlist = [/times(it),"east",height(0),tc_interp(it,:,g3(1),g3(0))/] 
     elist = [/times(it),"west",height(0),tc_interp(it,:,g4(1),g4(0))/]
     ;print_table(alist, format1) 
     write_table(txt_filename, "a", alist, format1)
     write_table(txt_filename, "a", blist, format1)
     write_table(txt_filename, "a", clist, format1)
     write_table(txt_filename, "a", dlist, format1)
     write_table(txt_filename, "a", elist, format1)

   end do

;-- WRITE WIND TO FILES
   print("Writing Wind to file!")
   do it = 0,ntimes-1
     print("Working on time: " + times(it) ) 

     ;-- dir10/spd10 
     ;list_1 = [/times(it),"blindern","10",spd10(it,munch(1),munch(0)),dir10(it,munch(1),munch(0))/] 
     ;list_2 = [/times(it),"north","10",spd10(it,g1(1),g1(0)),dir10(it,g1(1),g1(0))/] 
     ;list_3 = [/times(it),"south","10",spd10(it,g2(1),g2(0)),dir10(it,g2(1),g2(0))/] 
     ;list_4 = [/times(it),"east","10",spd10(it,g3(1),g3(0)),dir10(it,g3(1),g3(0))/] 
     ;list_5 = [/times(it),"west","10",spd10(it,g4(1),g4(0)),dir10(it,g4(1),g4(0))/]
     ;write_table(txt_filename2, "a", list_1, "%s,%s,%s,%g,%g")
     ;write_table(txt_filename2, "a", list_2, "%s,%s,%s,%g,%g")
     ;write_table(txt_filename2, "a", list_3, "%s,%s,%s,%g,%g")
     ;write_table(txt_filename2, "a", list_4, "%s,%s,%s,%g,%g")
     ;write_table(txt_filename2, "a", list_5, "%s,%s,%s,%g,%g")

     ;-- dir/spd 
     list_a = [/times(it),"blindern","26.5",spd(it,0,munch(1),munch(0)),dir(it,0,munch(1),munch(0))/] 
     list_b = [/times(it),"north","26.5",spd(it,0,g1(1),g1(0)),dir(it,0,g1(1),g1(0))/] 
     list_c = [/times(it),"south","26.5",spd(it,0,g2(1),g2(0)),dir(it,0,g2(1),g2(0))/] 
     list_d = [/times(it),"east","26.5",spd(it,0,g3(1),g3(0)),dir(it,0,g3(1),g3(0))/] 
     list_e = [/times(it),"west","26.5",spd(it,0,g4(1),g4(0)),dir(it,0,g4(1),g4(0))/]
     write_table(txt_filename2, "a", list_a, "%s,%s,%s,%g,%g")
     write_table(txt_filename2, "a", list_b, "%s,%s,%s,%g,%g")
     write_table(txt_filename2, "a", list_c, "%s,%s,%s,%g,%g")
     write_table(txt_filename2, "a", list_d, "%s,%s,%s,%g,%g")
     write_table(txt_filename2, "a", list_e, "%s,%s,%s,%g,%g")


   end do

end
  
