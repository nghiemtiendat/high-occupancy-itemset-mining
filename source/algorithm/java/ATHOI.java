import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ATHOI {

    // path to source file
    private String srcFile;
    // number of high occupancy itemsets
    private int numHOIs;
    // minimum occupancy threshold
    private double minOcp;
    // length of transactions
    private List<Integer> lenTrans;
    // high occupancy itemsets
    private Map<Set<String>, Double> HOIs;

    public ATHOI(String srcFile, int numHOIs) {
        this.srcFile = srcFile;
        this.numHOIs = numHOIs;
        this.minOcp = 0;
        this.lenTrans = new ArrayList<>();
        this.HOIs = new HashMap<>(numHOIs);
    }

    private double getUBO(Set<Integer> STSet) {
        // scan support transaction set
        Map<Integer, Integer> lenList = new HashMap<>();
        for (int trans : STSet) {
            int length = this.lenTrans.get(trans);
            lenList.put(length, lenList.getOrDefault(length, 0) + 1);
        }

        // calculate upper-bound occupancy
        List<Integer> l = new ArrayList<>(lenList.keySet());
        double maxUBO = 0;
        for (int x = 0; x < l.size(); x++) {
            int lx = l.get(x);
            double UBO = 0;
            for (int i = x; i < l.size(); i++) {
                int li = l.get(i);
                UBO += lenList.get(li) * ((double) lx / li);
            }
            if (UBO > maxUBO) {
                maxUBO = UBO;
            }
        }
        return maxUBO;
    }

    private double getOcp(Set<String> itemset, Set<Integer> STSet) {
        double ocp = 0;
        for (int trans : STSet) {
            ocp += (double) itemset.size() / this.lenTrans.get(trans);
        }
        return ocp;
    }

    private Map<Set<String>, Set<Integer>> mine1Itemset(
        Map<Set<String>, Set<Integer>> STSet) {
        Map<Set<String>, Set<Integer>> C1 = new HashMap<>();
        for (Set<String> P : STSet.keySet()) {
            Set<Integer> STSetP = STSet.get(P);
            if (STSetP.size() > this.minOcp) {
                double ocp = this.getOcp(P, STSetP);
                if (ocp > this.minOcp) {
                    // if number of high occupancy itemsets is not enough
                    // insert new itemset into HOIs
                    if (this.HOIs.size() < this.numHOIs) {
                        this.HOIs.put(P, ocp);
                    // otherwise
                    } else {
                        // find itemset with smallest occupancy value and remove
                        Set<String> key = Collections.min(this.HOIs.entrySet(),
                            Map.Entry.comparingByValue()).getKey();
                        this.HOIs.remove(key);
                        // insert new itemset into HOIs
                        this.HOIs.put(P, ocp);
                        // recalculate minimum occupancy threshold
                        this.minOcp = Collections.min(this.HOIs.values());
                    }
                }
                double UBO = this.getUBO(STSetP);
                if (UBO > this.minOcp) {
                    C1.put(P, STSetP);
                }
            }
        }
        return C1;
    }

    private void mineDepth(Map<Set<String>, Set<Integer>> C) {
        List<Set<String>> itemsets = new ArrayList<>(C.keySet());
        for (int i = 0; i < itemsets.size(); i++) {
            Map<Set<String>, Set<Integer>> Ck = new HashMap<>();
            Set<String> P1 = itemsets.get(i);
            for (int j = i + 1; j < itemsets.size(); j++) {
                Set<String> P2 = itemsets.get(j);
                Set<Integer> STSetP = new HashSet<>(C.get(P1));
                STSetP.retainAll(C.get(P2));
                if (STSetP.size() > this.minOcp) {
                    Set<String> P = new HashSet<>(P1);
                    P.addAll(P2);
                    double ocp = this.getOcp(P, STSetP);
                    if (ocp > this.minOcp) {
                        // if number of high occupancy itemsets is not enough
                        // insert new itemset into HOIs
                        if (this.HOIs.size() < this.numHOIs) {
                            HOIs.put(P, ocp);
                        // otherwise
                        } else {
                            // find itemset with smallest occupancy value and remove
                            Set<String> key = Collections.min(this.HOIs.entrySet(),
                                Map.Entry.comparingByValue()).getKey();
                            this.HOIs.remove(key);
                            // insert new itemset into HOIs
                            this.HOIs.put(P, ocp);
                            // recalculate minimum occupancy threshold
                            this.minOcp = Collections.min(this.HOIs.values());
                        }
                    }
                    double UBO = this.getUBO(STSetP);
                    if (UBO > this.minOcp) {
                        Ck.put(P, STSetP);
                    }
                }
            }
            if (Ck.size() > 1) {
                this.mineDepth(Ck);
            }
        }
    }

    public void run() {
        // scan database to obtain support transaction set of each 1-itemset
        // and length of each transaction
        Map<Set<String>, Set<Integer>> STSet = new HashMap<>();
        try (BufferedReader br = new BufferedReader(new FileReader(this.srcFile))) {
            int i = 0;
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isEmpty()) {
                    this.lenTrans.add(0);
                } else {
                    String[] trans = line.split("\\s+");
                    this.lenTrans.add(trans.length);
                    for (String item : trans) {
                        Set<String> itemset = Set.of(item);
                        if (!STSet.containsKey(itemset)) {
                            STSet.put(itemset, new HashSet<>());
                        }
                        STSet.get(itemset).add(i);
                    }
                }
                i++;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // mine 1-itemsets
        Map<Set<String>, Set<Integer>> C1 = this.mine1Itemset(STSet);

        // mine k-itemsets by using depth first search
        if (C1.size() > 1) {
            this.mineDepth(C1);
        }
    }

    public void export(String desFile) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(desFile))) {
            String text;
            for (Map.Entry<Set<String>, Double> hoi : this.HOIs.entrySet()) {
                text = String.format("%s %.2f", hoi.getKey(), hoi.getValue());
                bw.write(text);
                bw.newLine();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}