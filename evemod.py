

def eve_bases_generator(n):
    return [random.randint(0,1) for _ in range(n)]

def eve_attack(qc, n, attack_prob):
    eve_bases = eve_bases_generator(n)

    backend = Aer.get_backend('qasm_simulator')

    for i in range(n):
        if random.random() < attack_prob:

          
            if eve_bases[i] == 1:
                qc.h(i)

      
            qc.measure(i, i)
            job = execute(qc, backend, shots=1)
            res = list(job.result().get_counts().keys())[0]
            b = int(res[n-1-i])

        
            qc.reset(i)

          
            if eve_bases[i] == 0:
                if b == 1:
                    qc.x(i)
            else:
                if b == 0:
                    qc.h(i)
                else:
                    qc.x(i)
                    qc.h(i)

    return qc, eve_bases
