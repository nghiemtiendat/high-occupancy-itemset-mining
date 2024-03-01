import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class HEP {
    
    // path to source file
    private String srcFile;
    // minimum occupancy threshold
    private double minOcp;
    // high occupancy itemsets
    private Map<Set<String>, Double> HOIs;

    public HEP(String srcFile, double minOcp) {
        this.srcFile = srcFile;
        this.minOcp = minOcp;
        this.HOIs = new HashMap<>();
    }

    private double getUBO(Set<List<Integer>> STSet) {
        // scan support transaction set
        Map<Integer, Integer> lenList = new HashMap<>();
        for (List<Integer> trans : STSet) {
            int length = trans.get(1);
            lenList.put(length, lenList.getOrDefault(length, 0) + 1);
        }
        
        // calculate upper-bound occupancy
        List<Integer> l =  new ArrayList<>(lenList.keySet());
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

    private double getOcp(Set<String> itemset, Set<List<Integer>> STSet) {
        double ocp = 0;
        for (List<Integer> trans : STSet) {
            ocp += (double) itemset.size() / trans.get(1);
        }
        return ocp;
    }

    public void run() {
        // scan database to obtain occupancy-list of each 1-itemset
        Map<Set<String>, Set<List<Integer>>> ocpList = new HashMap<>();
        try (BufferedReader br = new BufferedReader(new FileReader(this.srcFile))) {
            int i = 0;
            String line;
            while ((line = br.readLine()) != null) {
                if (!line.isEmpty()) {
                    String[] trans = line.split("\\s+");
                    for (String item : trans) {
                        Set<String> itemset = Set.of(item);
                        if (!ocpList.containsKey(itemset)) {
                            ocpList.put(itemset, new HashSet<>());
                        }
                        List<Integer> lenTrans = List.of(i, trans.length);
                        ocpList.get(itemset).add(lenTrans);
                    }
                }
                i++;
            }
            this.minOcp *= i;
        } catch (IOException e) {
            e.printStackTrace();
        }

        // mine 1-itemsets
        Map<Set<String>, Set<List<Integer>>> C1 = new HashMap<>();
        for (Set<String> P : ocpList.keySet()) {
            Set<List<Integer>> STSetP = ocpList.get(P);
            if (STSetP.size() >= this.minOcp) {
                double UBO = this.getUBO(STSetP);
                if (UBO >= this.minOcp) {
                    C1.put(P, STSetP);
                    double ocp = this.getOcp(P, STSetP);
                    if (ocp >= this.minOcp) {
                        this.HOIs.put(P, ocp);
                    }
                }
            }
        }

        // mine k-itemsets
        for (int k = 2; C1.size() > 1; k++) {
            Map<Set<String>, Set<List<Integer>>> C = new HashMap<>();
            Set<Set<String>> itemsets = C1.keySet();
            Set<Set<String>> checked = new HashSet<>();
            for (Set<String> P1 : itemsets) {
                for (Set<String> P2 : itemsets) {
                    Set<String> P = new HashSet<>(P1);
                    P.addAll(P2);
                    if (P.size() == k && !checked.contains(P)) {
                        Set<List<Integer>> STSetP = new HashSet<>(C1.get(P1));
                        STSetP.retainAll(C1.get(P2));
                        if (STSetP.size() >= this.minOcp) {
                            double UBO = this.getUBO(STSetP);
                            if (UBO >= this.minOcp) {
                                C.put(P, STSetP);
                                double ocp = this.getOcp(P, STSetP);
                                if (ocp >= this.minOcp) {
                                    this.HOIs.put(P, ocp);
                                }
                            }
                        }
                        checked.add(P);
                    }
                }
            }
            C1 = C;
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