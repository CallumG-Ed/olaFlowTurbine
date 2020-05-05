import os

for file in os.listdir():
    
    if file.startswith('Extrap'):
        
        Re = file[11:-3]
        b1 = Re.find('_')
        b2 = Re.find('.')
        Re = '0' + Re[b1:b2]
        
        
        out  = open('NACA_63418_Re'+Re, 'w')
        out.write('// Re = 0.' + Re[2:] + ' \n')
        out.write('// (alpha_deg cl cd)\n')

        with open(file) as f:
            for i, line in enumerate(f):
                
                entries = line.split()
                rline   = '(' + entries[0] + '\t' + entries[1] + '\t' + entries[2] + ')\n'
                out.write(rline)
       
        f.close()
        out.close()
