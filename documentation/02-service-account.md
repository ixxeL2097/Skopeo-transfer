## 02 - Service account 

### OpenShift

To give access to skopeo script to your registry and allow the script to push images, you need to create a **dedicated ServiceAccount**.

Let's create ServiceAccount named **skopeo** (put it in the namespace of your choice, in this example namespace default) :

```console
[root@workstation ~]$ oc create sa skopeo
serviceaccount/skopeo created
```

Collect the skopeo ServiceAccount token :

```console
[root@workstation ~]$ oc get secrets -o jsonpath='{range .items[?(@.metadata.annotations.kubernetes\.io/service-account\.name=="skopeo")]}{.metadata.annotations.openshift\.io/token-secret\.value}{end}' | tee skopeo-token
```

or simpler :

```console
[root@workstation ~]$ oc sa get-token skopeo -n default
```

Now you have to give cluster wide permission to this ServiceAccount to be able to push/pull images in any namespace of the cluster :

Cluster-wide push/pull permissions :
```
[root@workstation ~]$ oc adm policy add-cluster-role-to-user system:image-builder system:serviceaccount:default:skopeo
clusterrole.rbac.authorization.k8s.io/system:image-builder added: "system:serviceaccount:default:skopeo"
```

After this, you can use your skopeo script properly.

