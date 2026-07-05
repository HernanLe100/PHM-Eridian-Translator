# bucket_vp_tree.py - Hernan Le

# This module implements a vantage point tree data structure with buckets. 

# Each leaf node has a bucket that stores a list of items. 
# Once the length of the list exceeds a certain amount, the list splits 
# so that half of the items are within a calculated distance to the node's 
# vantage point. One item from each half is then chosen to become the vantage 
# point for the respective child node.
# Buckets are used to balance between cost of adding to the tree and searching the tree.

# ----------------------------------------------------------------------

from typing import Callable
import numpy as np

# ----------------------------------------------------------------------

# implements the functionality for individual nodes
class VP_Node:
    # Constructor requires a distance function to specify 
    # how to calculate distance between items.
    # If provided a specific data dict, the node is built according to the data.
    def __init__( self, 
            dist_func: Callable[[object, object],float], 
            data:dict=None
        ):
        
        self._dist_func = dist_func 
        
        self._vantage_point = None
        self._radius = -1
        
        self._bucket = [] # by default, a new node is a leaf 
        
        self._left = None
        self._right = None
        
        if data: # data is not None and not empty
            if "bucket" in data: # is leaf 
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
    
    def is_leaf(self) -> bool:
        # node is leaf iff bucket is not None
        # also note: as a leaf, radius is -1 (not set yet) and left and right are None
        return self._bucket is not None
    
    def get_bucket(self):
        return self._bucket
    def bucket_length(self) -> int:
        return len(self._bucket)
    
    def get_vantage_point(self):
        return self._vantage_point
    def get_radius(self):
        return self._radius
    def get_left(self):
        return self._left
    def get_right(self):
        return self._right
    
    # Adds value to node. 
    # The first value added to a node becomes the vantage point
    # Otherwise, the value is appended to a list.
    def add(self, value):
        if self._vantage_point is None:
            self._vantage_point = value
        else:
            self._bucket.append(value)
        
    # Calculates the distances to the vantage point from each item in the bucket 
    # and finds the median distance.
    # Returns the index of the median distance and the list of distances.
    def _get_median(self) -> int:
        dist_bucket = []
        for v in self._bucket:
            dist_bucket.append( self._dist_func(self._vantage_point, v) )
        sorted_indexes = np.argsort(dist_bucket)
        
        # lean toward lower if length is even
        median_index = ((len(sorted_indexes)+1) // 2) - 1
        return sorted_indexes[median_index], dist_bucket
    
    # splits the node along its median, creating left and right child nodes
    def split(self):
        median_index, dist_bucket = self._get_median()
        
        # make radius the median distance
        self._radius = dist_bucket[median_index]
        
        self._left = VP_Node(self._dist_func)
        self._right = VP_Node(self._dist_func)
        
        for i in range(len(self._bucket)):
            # distances less than or equal to the radius go left
            if dist_bucket[i] <= self._radius:
                self._left.add(self._bucket[i])
            else:
                self._right.add(self._bucket[i])
        
        # bucket no longer in use after splitting
        self._bucket = None
    
    # returns dict representation of this node
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

# implements the functionality for bucket VP tree
class Bucket_VP_Tree:
    # Constructor requires a distance function to specify 
    # how to calculate distance between items.
    # Specific bucket capacity can be specified. Once a bucket's capacity is exceeded, it will split.
    # If provided a specific data dict, the tree is built according to the data.
    def __init__(self, 
            dist_func: Callable[[object, object],float], 
            bucket_capacity = 10,
            data = None
        ):
        
        self._dist_func = dist_func
        self._bucket_capacity = bucket_capacity
        self._root = VP_Node(dist_func, data = data)
        
    # adds value to tree
    def add(self, value):
        self._add(self._root, value)
    
    # recursive helper function to add to tree
    def _add(self, node:VP_Node, value):
        if node.is_leaf() :
            node.add(value)
            if node.bucket_length() > self._bucket_capacity:
                node.split()
        else:
            dist = self._dist_func(node.get_vantage_point(), value)
            if dist <= node.get_radius():
                self._add(node.get_left(), value)
            else: 
                self._add(node.get_right(), value)
    
    # Searches for item nearest to query value.
    # Returns a dict consisting of the nearest value and distance from the query.
    # If bound is given, the function searches for the nearest value that 
    # has a distance less than the bound.
    def nearest(self, value, bound=np.inf):
        best = {"value": None, "dist": bound}
        return self._nearest(self._root, value, best)
    
    # recursive helper function to search for nearest value
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
    
    # returns dict representation of this tree
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
    
    

            
