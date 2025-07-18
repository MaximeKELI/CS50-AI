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
    """
    joint_probability_result = 1

    for person in people:
        person_gene_count = 1 if person in one_gene else 2 if person in two_genes else 0
        person_has_trait = True if person in have_trait else False

        if people[person]["mother"] != None and people[person]["father"] != None:
            mother_name = people[person]["mother"]
            father_name = people[person]["father"]

            # Calculates probability a parent passes down gene based on how many of the desired genes the parent has
            parent_gene_inheritance_probability = {}
            for parent_name in [mother_name, father_name]:
                if parent_name in one_gene:
                    parent_gene_inheritance_probability[parent_name] = 0.5
                elif parent_name in two_genes:
                    parent_gene_inheritance_probability[parent_name] = 1 - PROBS["mutation"]
                else:
                    parent_gene_inheritance_probability[parent_name] = PROBS["mutation"]

            if person_gene_count == 1:
                # Possibility in the cases that either mother passes down gene, father does not pass down gene and mother does not pass down gene, father passes down gene
                joint_probability_result *= (parent_gene_inheritance_probability[mother_name] * (1 - parent_gene_inheritance_probability[father_name]) +
                                             (1 - parent_gene_inheritance_probability[mother_name]) * parent_gene_inheritance_probability[father_name])
            elif person_gene_count == 2:
                # Possibility that mother and father passes down gene
                joint_probability_result *= parent_gene_inheritance_probability[mother_name] * parent_gene_inheritance_probability[father_name]
            else:
                # Possibility that mother and father do not pass down gene
                joint_probability_result *= (1 - parent_gene_inheritance_probability[mother_name]) * (1 - parent_gene_inheritance_probability[father_name])
        else:
            joint_probability_result *= PROBS["gene"][person_gene_count]

        joint_probability_result *= PROBS["trait"][person_gene_count][person_has_trait]

    return joint_probability_result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        person_gene_count = 1 if person in one_gene else 2 if person in two_genes else 0
        person_has_trait = True if person in have_trait else False

        probabilities[person]["gene"][person_gene_count] += p
        probabilities[person]["trait"][person_has_trait] += p

    # Updates probabilities input directly and does not have a return value


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for statistic in ["gene", "trait"]:
            statistic_probability_sum = sum(probabilities[person][statistic].values())

            for statistic_probability in probabilities[person][statistic]:
                probabilities[person][statistic][statistic_probability] /= statistic_probability_sum

    # Updates probabilities directly and does not have a return value


if __name__ == "__main__":
    main()