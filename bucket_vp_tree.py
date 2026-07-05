from typing import Callable
import numpy as np

class VP_Node:
    
    def __init__( self, 
            dist_func: Callable[[object, object],float], 
            data=None
        ):
        
        self._dist_func = dist_func
        
        self._vantage_point = None
        self._radius = -1
        
        self._bucket = []
        
        self._left = None
        self._right = None
        
        if data: # my_dict is not None and not empty
            if "bucket" in data: 
                self._bucket = data["bucket"]
                self._vantage_point = data["vantage point"]
                self._radius = -1
                self._left = None
                self._right = None
            else:
                self._vantage_point = data["vantage point"]
                self._radius = data["radius"]
                self._bucket = None
                
                self._left = VP_Node(dist_func=self._dist_func, data=data["left"])
                self._right = VP_Node(dist_func=self._dist_func, data=data["right"])
    
    def get_bucket(self):
        return self._bucket
    def bucket_length(self) -> int:
        return len(self._bucket)
    
    def is_leaf(self) -> bool:
        # node is leaf iff bucket is not None
        # also note: as a leaf, radius is -1 (not set yet) and left and right are None
        return self._left is None and self._right is None 
    
    def get_vantage_point(self):
        return self._vantage_point
    def get_radius(self):
        return self._radius
    def get_left(self):
        return self._left
    def get_right(self):
        return self._right
        
    def add(self, value):
        if self._vantage_point is None:
            self._vantage_point = value
        else:
            self._bucket.append(value)
        
    def _get_median(self) -> int:
        dist_bucket = []
        for v in self._bucket:
            dist_bucket.append( self._dist_func(self._vantage_point, v) )
        sorted_indexes = np.argsort(dist_bucket)
        
        # lean toward lower if length is even
        median_index = ((len(sorted_indexes)+1) // 2) - 1
        return sorted_indexes[median_index], dist_bucket
        
    def split(self):
        median_index, dist_bucket = self._get_median()
        
        # make radius the median distance
        self._radius = dist_bucket[median_index]
        
        self._left = VP_Node(self._dist_func)
        self._right = VP_Node(self._dist_func)
        
        for i in range(len(self._bucket)):
            if dist_bucket[i] <= self._radius:
                self._left.add(self._bucket[i])
            else:
                self._right.add(self._bucket[i])
        
        # bucket no longer in use after splitting
        self._bucket = None
        
    def to_dict(self):
        if self.is_leaf():
            return {
                "vantage point": self._vantage_point,
                "bucket" : self._bucket,
            }
        else:
            return {
                "vantage point": self._vantage_point,
                "radius": self._radius,
                "left" : self._left.to_dict(),
                "right" : self._right.to_dict(),
            }
            

# ----------------------------------------------------------------------

class Bucket_VP_Tree:
    
    def __init__(self, 
            dist_func: Callable[[object, object],float], 
            bucket_capacity = 10,
            data = None
        ):
        
        self._dist_func = dist_func
        self._bucket_capacity = bucket_capacity
        self._root = VP_Node(dist_func, data = data)
        
    
    def add(self, value):
        self._add(self._root, value)
        
    def _add(self, node:VP_Node, value):
        if node.is_leaf() :
            if node.bucket_length() == self._bucket_capacity:
                node.split()
                self._add(node, value)
            else:
                node.add(value)
        else:
            dist = self._dist_func(node.get_vantage_point(), value)
            if dist <= node.get_radius():
                self._add(node.get_left(), value)
            else: 
                self._add(node.get_right(), value)
    
    def nearest(self, value, bound=np.inf):
        best = {"value": None, "dist": bound}
        return self._nearest(self._root, value, best)
    
    def _nearest(self, node:VP_Node, value, best):
        if node.is_leaf():
            if node.get_vantage_point() is not None: 
                dist = self._dist_func(node.get_vantage_point(), value)
                if dist < best["dist"]:
                    best["dist"] = dist
                    best["value"] = node.get_vantage_point()
            for v in node.get_bucket():
                dist = self._dist_func(v, value)
                if dist < best["dist"]:
                    best["dist"] = dist
                    best["value"] = v
            return best
        else:
            dist = self._dist_func(node.get_vantage_point(), value)
            if dist < best["dist"]:
                best["dist"] = dist
                best["value"] = node.get_vantage_point()

            if dist <= node.get_radius():
                # inside radius
                best = self._nearest(node.get_left(), value, best )
                
                # also check outside if possible to find closer match
                if dist + best["dist"] > node.get_radius():
                    best = self._nearest(node.get_right(), value, best)
                
            else: 
                # outside radius
                best = self._nearest(node.get_right(), value, best)
                
                # also check inside if possible to find closer match
                if dist - best["dist"] <= node.get_radius():
                    best = self._nearest(node.get_left(), value, best)
            return best
    
    def to_dict(self):
        return self._root.to_dict()
    
# ----------------------------------------------------------------------

    
def main():
    bvp = Bucket_VP_Tree(lambda a,b: (a-b)**2, bucket_capacity=2)
    
    bvp.add(1)
    bvp.add(2)
    bvp.add(3)
    bvp.add(4)
    bvp.add(5)
    bvp.add(4.5)
    print( bvp.nearest(4.4) )
    data = bvp.to_dict()
    print(data)
    
    bvp2 = Bucket_VP_Tree(lambda a,b: (a-b)**2, bucket_capacity=2, data = data)
    print(bvp2.to_dict())
    
    import json
    print(json.loads(json.dumps(bvp2.to_dict())))
    

if __name__ == "__main__":
    main()
    
    

            
