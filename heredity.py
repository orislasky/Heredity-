import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue
        
        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
        
        Step 1 - Identify who has 0 genes
        Step 2 for person in people:
        Start with all people who dont have parents
        Step 3 If Person has 0 gene- 
            - If Person doesnt have parents && no Trait then  PROBS["gene"][0] * PROBS["trait"][0][False]
              If P0 doesnt have parents && YES Trait then  PROBS["gene"][0] * PROBS["trait"][0][True]
        Step 4 If Person has 1 gene- 
            - If Person doesnt have parents && no Trait then  PROBS["gene"][1] * PROBS["trait"][1][False]
              If P0 doesnt have parents && YES Trait then  PROBS["gene"][1] * PROBS["trait"][1][True]
        Step 5 - If person has 2 genes.....
        
        If person has parents
        
        
        
        Loop all people who have parents and break into several cases:

            child has one gene
            
                from mother, so not from father
            
                    mother cases (p1)
            
                        has one gene: 0.5 (pass one gene)
            
                        has two gene: 0.99 (minus mutation)
            
                        has no gene: 0.01(mutation)
            
                    father cases (p2)
            
                        has one gene: 0.5 (pass no gene)
            
                        has two gene: 0.01 (mutation)
            
                        has no gene: 0.99 (minus mutation)
            
                from father, so not from mother
                        father cases (p3)
            
                            has one gene: 0.5 (pass one gene)
            
                            has two gene: 0.99 (minus mutation)
            
                            has no gene: 0.01(mutation)
                        mother cases(p4)
                            has one gene: 0.5 (pass no gene)
            
                            has two gene: 0.01 (mutation)
            
                            has no gene: 0.99 (minus mutation)
            
                    (like above, but exchange the role) (p3 and p4)
                    what does this mean??????
            
                => ( p1 x p2 + p3 x p4 ) x trait
            
            child has two gene (parents should pass one gene individually)
            
                mother (p1)
            
                    has one gene: 0.5 (pass one gene)
            
                    has two gene: 0.99 (minus mutation) 
            
                    has no gene: 0.01 (mutation)
            
                father (p2)
            
                    (same as above)
            
                => ( p1 x p2 ) x trait
            
            child has no gene (parents should not pass gene)
            
                mother (p1)
            
                    has one gene: 0.5 (pass no gene)
            
                    has two gene: 0.01 (mutation)
            
                    has no gene: 0.99(except mutation)
            
                father (p2)
            
                    (same as above)
            
                => ( p1 x p2 ) x trait


        
        New Algorithm
        Loop all people who have parents and break into several cases:

            child has one gene
            
                from mother, so not from father
            
                    mother cases (p1)
            
                        has one gene: 0.5 (pass one gene)
            
                        has two gene: 0.99 (minus mutation)
            
                        has no gene: 0.01(mutation)
            
                    father cases (p2)
            
                        has one gene: 0.5 (pass no gene)
            
                        has two gene: 0.01 (mutation)
            
                        has no gene: 0.99 (minus mutation)
            
                from father, so not from mother
                        father cases (p3)
            
                            has one gene: 0.5 (pass one gene)
            
                            has two gene: 0.99 (minus mutation)
            
                            has no gene: 0.01(mutation)
                        mother cases(p4)
                            has one gene: 0.5 (pass no gene)
            
                            has two gene: 0.01 (mutation)
            
                            has no gene: 0.99 (minus mutation)
            
                    (like above, but exchange the role) (p3 and p4)
                    what does this mean??????
            
                => ( p1 x p2 + p3 x p4 ) x trait
            
            child has two gene (parents should pass one gene individually)
            
                mother (p1)
            
                    has one gene: 0.5 (pass one gene)
            
                    has two gene: 0.99 (minus mutation) 
            
                    has no gene: 0.01 (mutation)
            
                father (p2)
            
                    (same as above)
            
                => ( p1 x p2 ) x trait
            
            child has no gene (parents should not pass gene)
            
                mother (p1)
            
                    has one gene: 0.5 (pass no gene)
            
                    has two gene: 0.01 (mutation)
            
                    has no gene: 0.99(except mutation)
            
                father (p2)
            
                    (same as above)
            
                => ( p1 x p2 ) x trait
        
        
        
        
    """
    calculation=1.0
    zero_gene=set()
    for person in people:
        if person not in one_gene and person not in two_genes:
            print("********************this is person", person)
            zero_gene.add(person)
    print("zero gene", zero_gene)
    print("one gene", one_gene)
    print("2 genes",  two_genes)
    print("have trait",have_trait)
    
    '''       
    for person in zero_gene:
        if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==0:
            calculation=PROBS["gene"][0] * PROBS["trait"][0][False]*calculation
            print("zero gene, no parent, no trait", calculation)
            print("person - ", person)
        if person[1] is not None  and person[2] is not None and person[3]==1:
            print("b")
            calculation=PROBS["gene"][0] * PROBS["trait"][0][True]*calculation
    for person in one_gene:
        print ("one gene")
        print("person - ", people[person])
        if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==0:
            print("one gene, no parent, no trait", calculation)
            print("person - ", people[person])
            calculation=PROBS["gene"][1] * PROBS["trait"][1][False]*calculation
        if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==1:
            print("********one gene, no parent, YES trait", calculation)
            print("person - ", people[person])
            calculation=PROBS["gene"][1] * PROBS["trait"][1][True]*calculation
        
    for person in two_genes:
        print ("two genes")
        print("person - ", people[person])
        if person[1] is not None  and person[2] is not None and person[3]==0:
            print("two gene, no parent, no trait", calculation)
            print("person - ", people[person])
            calculation=PROBS["gene"][2] * PROBS["trait"][2][False]*calculation
        if person[1] is not None  and person[2] is not None and person[3]==1:
            print("f")
            calculation=PROBS["gene"][2] * PROBS["trait"][2][True]*calculation
        print(calculation*5)
    '''
    for person in people:
        counter=0
        if person in one_gene:
            #calculatign if the has no parents:
            if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==0:
                print("one gene, no parent, no trait", calculation)
                print("person - ", people[person])
                calculation=PROBS["gene"][1] * PROBS["trait"][1][False]*calculation
                counter+=1
            if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==1:
                print("********one gene, no parent, YES trait", calculation)
                print("person - ", people[person])
                calculation=PROBS["gene"][1] * PROBS["trait"][1][True]*calculation
                counter+=1
            if counter==0:
                '''
                child has one gene
            
                from mother, so not from father
            
                    mother cases (p1)
            
                        has one gene: 0.5 (pass one gene)
            
                        has two gene: 0.99 (minus mutation)
            
                        has no gene: 0.01(mutation)
            
                    father cases (p2)
            
                        has one gene: 0.5 (pass no gene)
            
                        has two gene: 0.01 (mutation)
            
                        has no gene: 0.99 (minus mutation)
            
                from father, so not from mother
                        father cases (p3)
            
                            has one gene: 0.5 (pass one gene)
            
                            has two gene: 0.99 (minus mutation)
            
                            has no gene: 0.01(mutation)
                        mother cases(p4)
                            has one gene: 0.5 (pass no gene)
            
                            has two gene: 0.01 (mutation)
            
                            has no gene: 0.99 (minus mutation)
            
                    (like above, but exchange the role) (p3 and p4)
                    what does this mean??????
            
                => ( p1 x p2 + p3 x p4 ) x trait
                '''
                #chekning if came from mom and not from dad:
                if people[person]["mother"] in zero_gene:
                    p1=0.01
                    p4=0.99
                if people[person]["father"] in zero_gene:
                    p2=0.99
                    p3=0.01
                if people[person]["mother"] in one_gene:
                    p1=0.5
                    p4=0.5
                if people[person]["father"] in one_gene:
                    p2=0.5
                    p3=0.5
                if people[person]["mother"] in two_genes:
                    p1=0.99
                    p4=0.01
                if people[person]["father"] in two_genes:
                    p2=0.01
                    p3=0.99
                if person in have_trait:
                    calculation=(p1*p2+p3*p4)*PROBS["trait"][1][True]*calculation
                else:
                    calculation=(p1*p2+p3*p4)*PROBS["trait"][1][False]*calculation
                 
                
        if person in two_genes:
            if people[person]["mother"] is not None  and people[person]["father"] is not None and people[person]["trait"]==0:
                print("two gene, no parent, no trait", calculation)
                print("person - ", people[person])
                calculation=PROBS["gene"][2] * PROBS["trait"][2][False]*calculation
                counter+=1
            if people[person]["mother"] is not None  and people[person]["father"] is not None and people[person]["trait"]==1:
                calculation=PROBS["gene"][2] * PROBS["trait"][2][True]*calculation
                counter+=1
            if counter==0:
            #UNIMPLEMENTED
                #calculating the genes of mom
                p1=1.0
                p2=1.0
                if people[person]["mother"] in zero_gene:
                    p1= 0.01
                if people[person]["mother"] in one_gene:
                    p1=0.5
                if people[person]["mother"] in two_genes:
                    p1=0.99
                #calculating the prob for gene for father:
                if people[person]["father"] in zero_gene:
                    p2=0.01
                if people[person]["father"] in one_gene:
                    p2=0.5
                if people[person]["father"] in two_genes:
                    p2=0.99
                if person in have_trait:
                    calculation=(p1*p2)*PROBS["trait"][2][True]*calculation
                else:
                    calculation=(p1*p2)*PROBS["trait"][2][False]*calculation
            
            
        if person in zero_gene:
            if people[person]["mother"] is  None  and people[person]["father"] is  None and people[person]["trait"]==0:
                calculation=PROBS["gene"][0] * PROBS["trait"][0][False]*calculation
                counter+=1
                print("zero gene, no parent, no trait", calculation)
                print("person - ", person)
            if people[person]["mother"] is not None  and people[person]["father"] is not None and people[person]["trait"]==1:
                print("b")
                calculation=PROBS["gene"][0] * PROBS["trait"][0][True]*calculation
                counter+=1
            ## missing scenario if they have parents
            if counter==0:
                #calculating the genes of mom
                if people[person]["mother"] in zero_gene:
                    p1= 0.99
                if people[person]["mother"] in one_gene:
                    p1=0.5
                if people[person]["mother"] in two_genes:
                    p1=0.01
                #calculating the prob for gene for father:
                if people[person]["father"] in zero_gene:
                    p2=0.99
                if people[person]["father"] in one_gene:
                    p2=0.5
                if people[person]["father"] in two_genes:
                    p2=0.01
                if person in have_trait:
                    calculation=(p1*p2)*PROBS["trait"][0][True]*calculation
                else:
                    calculation=(p1*p2)*PROBS["trait"][0][False]*calculation
        
            
        
        
        
            
                    
                
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #making a new set for all the people that have no parents:

    no_Parents=set()
    mother_cal=1.0
    father_cal=1.0
    return calculation
    ''' for person in people:
        if person[1] is None and person[2] is None:
            no_Parents.add(person)
    for person in no_Parents:
        mother_cal=1.0
        father_cal=1.0
        if person in one_gene:
            print("got in to one_gene")
            #checking if it came from mom:
            mother_cal*= 0.5*0.99*0.01
            mother_cal*=0.01*0.99*0.5
            #if came from father and not from mom:
            father_cal*= mother_cal
            if person in have_trait():
                calculation*=(mother_cal+father_cal)*PROBS["trait"][1][True]
            else:
                calculation*=(mother_cal+father_cal)*PROBS["trait"][1][False]
        if person in two_genes:
            print("got in to two")
        
        
               #checjing if the gene came from mother:
            mother_cal*=0.5*0.99*0.01
            # and if it cma eform father
            father_cal*= 0.99*0.5*0.1
            if person in have_trait():
                print("got in to have trait")
                calculation*=(mother_cal+father_cal)*PROBS["trait"][1][True]
            else:
                calculation*=(mother_cal+father_cal)*PROBS["trait"][1][False]
        if person in have_trait:
            if person in zero_gene:
                calculation*= PROBS["trait"][0][True]
            if person in one_gene:
                calculation*= PROBS["trait"][1][True]
            if person in two_genes:
                calculation*= PROBS["trait"][2][True]
                
        '''
        
        
        #triying it one more time:
''' 
        for person in people:
            counter=0
            if person in one_gene:
                if person[1] is not None  and person[2] is not None and person[3]==0:
                    calculation=PROBS["gene"][1] * PROBS["trait"][1][False]*calculation
                    counter=counter+1
                if person[1] is not None  and person[2] is not None and person[3]==1:
                    calculation=PROBS["gene"][1] * PROBS["trait"][1][True]*calculation
                    counter=counter+1
                if counter>0:
                     #checking if it came from mom:
                    p1=0.5
                    p2=0.5
                    #if came from father and not from mom:
                    p3=0.5
                    p4=0.5
                    if person in have_trait():
                        calculation*=(p1*p2+p3*p4)*PROBS["trait"][1][True]
                    else:
                        calculation*=(p1*p2+p3*p4)*PROBS["trait"][1][False]
                if person in two_genes:
                    #if one from mom amd one from the dad:
                    if person[1] is not None  and person[2] is not None and person[3]==0:
                        calculation=PROBS["gene"][2] * PROBS["trait"][2][False]*calculation
                        counter=counter+1
                    if person[1] is not None  and person[2] is not None and person[3]==1:
                        calculation=PROBS["gene"][2] * PROBS["trait"][2][True]*calculation
                        counter=counter+1
                    if counter>0:
                        
                    '''
                    
                
            
''' 
    if person not in have_trait and person not in one_gene and person not in two_genes:
            print("got in to if of everything none!!")
            #calculate the prob he doesnt have a trait!!
            if person in zero_gene:
                calculation*= PROBS["trait"][0][False]
            if person in one_gene:
                calculation*= PROBS["trait"][1][False]
            if person in two_genes:
                calculation*= PROBS["trait"][2][False]
    '''        
    # print (calculation)       
    # return calculation

            
        
            
        
    
        
            
    
    #raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p
   
    #raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        
        #finding the factor to multiply for looking at the trait
        prob_sum= probabilities[person]["trait"][False]+probabilities[person]["trait"][True]
        factor= 1/prob_sum
        probabilities[person]["trait"][False]*=factor
        probabilities[person]["trait"][True]*=factor
        # ORI SEE WHAT I CHANGED ABOVE and implement below
        #finding the factor to multiply for looking at the geens
        prob_sum= probabilities[person]["gene"][1]+probabilities[person]["gene"][2]+probabilities[person]["gene"][0]
        factor= 1/prob_sum
        probabilities[person]["gene"][0]*=factor
        probabilities[person]["gene"][1]*=factor
        probabilities[person]["gene"][2]*=factor
        
    #raise NotImplementedError


if __name__ == "__main__":
    main()
