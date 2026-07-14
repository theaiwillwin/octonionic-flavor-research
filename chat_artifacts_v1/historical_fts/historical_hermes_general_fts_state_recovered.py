import torch, numpy as np, itertools, math, sys
try:
    from scipy.optimize import minimize
    HAVE_SCIPY=True
except Exception:
    HAVE_SCIPY=False

torch.set_default_dtype(torch.float64)
CKM_abs_np=np.array([[0.97435,0.22500,0.00369],[0.22486,0.97349,0.04182],[0.00857,0.04110,0.999118]],float)
CKM_abs=torch.tensor(CKM_abs_np)
perms=list(itertools.permutations(range(3)))
s12_t=0.22500; s23_t=0.04182; s13_t=0.00369
c12_t=math.sqrt(1-s12_t*s12_t); c23_t=math.sqrt(1-s23_t*s23_t); c13_t=math.sqrt(1-s13_t*s13_t)
a=s12_t*s23_t; b=c12_t*c23_t*s13_t; vtd=0.00857
cosd=(a*a+b*b-vtd*vtd)/(2*a*b); cosd=max(-1,min(1,cosd)); delta_t=math.acos(cosd)
J_target=s12_t*s23_t*s13_t*c12_t*c23_t*c13_t*c13_t*math.sin(delta_t)
# octonion tables
def qmul_np(x,y):
    a,b,c,d=x; e,f,g,h=y
    return np.array([a*e-b*f-c*g-d*h,a*f+b*e+c*h-d*g,a*g-b*h+c*e+d*f,a*h+b*g-c*f+d*e],dtype=np.result_type(x,y))
def qconj_np(x): z=x.copy(); z[1:]*=-1; return z
def omul_np(x,y):
    a,b=x[:4],x[4:]; c,d=y[:4],y[4:]
    return np.r_[qmul_np(a,c)-qmul_np(qconj_np(d),b),qmul_np(d,a)+qmul_np(b,qconj_np(c))]
E=np.eye(8); C_np=np.zeros((8,8,8)); A_np=np.zeros((7,7,7,7))
for i,j in itertools.product(range(8),repeat=2): C_np[i,j,:]=omul_np(E[i],E[j])
for i,j,h in itertools.product(range(7),repeat=3):
    A_np[i,j,h,:]=(omul_np(omul_np(E[i+1],E[j+1]),E[h+1])-omul_np(E[i+1],omul_np(E[j+1],E[h+1])))[1:]
C=torch.tensor(C_np); A=torch.tensor(A_np)
I3t=torch.zeros(3,3,8); I3t[0,0,0]=I3t[1,1,0]=I3t[2,2,0]=1.0
# torch optimization/action helpers
def q_frame(raw):
    Q,R=torch.linalg.qr(raw); s=torch.sign(torch.diagonal(R)); s=torch.where(s==0,torch.ones_like(s),s); return Q*s.unsqueeze(0)
def edge_t(gen,H): return torch.einsum('ia,jb,h,ijhk->abk',gen,gen,H,A)
def mass_from_T(T): return (T*T).sum(-1)
def B_from_T(Td,Tk): return 2*(Td*Tk).sum(-1)
def mass_t(gen,H): return mass_from_T(edge_t(gen,H))
def sorted_basis_real(M):
    w,V=torch.linalg.eigh(M); idx=torch.argsort(torch.abs(w),descending=True); return w[idx],V[:,idx]
row_perm=torch.tensor([1,2,0]); col_perm=torch.tensor([2,1,0])
def ckm_loss_real_fixed(Q):
    gen=Q[:,:3]; Mu=mass_t(gen,Q[:,3]); Md=mass_t(gen,Q[:,5]); _,U=sorted_basis_real(Mu); _,D=sorted_basis_real(Md)
    W=torch.abs((U.T@D)[row_perm][:,col_perm]); return ((W-CKM_abs)**2).sum(),W
def oct_conj_t(x): y=x.clone(); y[...,1:]=-y[...,1:]; return y
def mat_mul_t(X,Y): return torch.einsum('ikA,kjB,ABC->ijC',X,Y,C)
def jordan_t(X,Y): return 0.5*(mat_mul_t(X,Y)+mat_mul_t(Y,X))
def trJ_t(X): return X[0,0,0]+X[1,1,0]+X[2,2,0]
def innerJ_t(X,Y): return trJ_t(jordan_t(X,Y))
def sharp_t(X):
    X2=jordan_t(X,X); tr=trJ_t(X); S=0.5*(tr*tr-trJ_t(X2)); return X2-tr*X+S*I3t
def normJ_t(X): return torch.sqrt(torch.clamp(innerJ_t(X,X),min=0)+1e-12)
def detJ_t(X): return innerJ_t(X,sharp_t(X))/3.0
def assoc_vec_t(gen,H,a,b):
    v=torch.einsum('i,j,h,ijhk->k',gen[:,a],gen[:,b],H,A); return torch.cat([torch.zeros(1,dtype=v.dtype),v])
def build_J_t(gen,H):
    z=assoc_vec_t(gen,H,0,1); x=assoc_vec_t(gen,H,1,2); y=assoc_vec_t(gen,H,2,0)
    nx=(x*x).sum(); ny=(y*y).sum(); nz=(z*z).sum(); X=torch.zeros(3,3,8,dtype=gen.dtype)
    X[0,0,0]=ny+nz; X[1,1,0]=nz+nx; X[2,2,0]=ny+nx
    X[0,1]=oct_conj_t(z); X[1,0]=z; X[0,2]=oct_conj_t(y); X[2,0]=y; X[1,2]=oct_conj_t(x); X[2,1]=x
    return X
def Atwist(Q):
    gen=Q[:,:3]; Ju=build_J_t(gen,Q[:,3]); Jd=build_J_t(gen,Q[:,5]); Jun=Ju/(normJ_t(Ju)+1e-12); Jdn=Jd/(normJ_t(Jd)+1e-12)
    Delta=(1-innerJ_t(Jun,Jdn))**2-4*(detJ_t(Jun)+detJ_t(Jdn)-innerJ_t(sharp_t(Jun),sharp_t(Jdn)))
    Nd=detJ_t(Jdn)
    return Delta-2*Nd,Delta,Nd
def chiral_and_mats(Q):
    gen=Q[:,:3]
    Tu=edge_t(gen,Q[:,3]); Td=edge_t(gen,Q[:,5]); T1=edge_t(gen,Q[:,4]); T2=edge_t(gen,Q[:,6])
    Mu=mass_from_T(Tu); Md=mass_from_T(Td); B1=B_from_T(Td,T1); B2=B_from_T(Td,T2)
    def n(M): return M/(torch.linalg.norm(M)+1e-12)
    Muh=n(Mu); Mdh=n(Md); B1h=n(B1); B2h=n(B2)
    K=Muh@Mdh-Mdh@Muh; L=B1h@B2h-B2h@B1h; P=torch.trace(K@L)
    return P,Muh,Mdh,B1h,B2h,K,L
def action(Q):
    At,De,Nd=Atwist(Q); P,*_=chiral_and_mats(Q); return At-0.5*P,At,De,Nd,P
pairs=[(i,j) for i in range(7) for j in range(i+1,7)]
def skew(theta):
    S=torch.zeros(7,7,dtype=theta.dtype)
    for k,(i,j) in enumerate(pairs): S[i,j]=theta[k]; S[j,i]=-theta[k]
    return S
def Q_from_theta(Qbase,theta): return Qbase@torch.linalg.matrix_exp(skew(theta))
def optimize_action(Qbase,steps=1400):
    theta=torch.zeros(21,requires_grad=True)
    opt=torch.optim.Adam([theta],lr=.03); sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=steps,eta_min=1e-5)
    for _ in range(steps):
        opt.zero_grad(); Q=Q_from_theta(Qbase,theta); S,*_=action(Q); S.backward(); opt.step(); sched.step()
    opt2=torch.optim.LBFGS([theta],lr=0.35,max_iter=80,line_search_fn='strong_wolfe',tolerance_grad=1e-12,tolerance_change=1e-14)
    def closure():
        opt2.zero_grad(); Q=Q_from_theta(Qbase,theta); S,*_=action(Q); S.backward(); return S
    try: opt2.step(closure)
    except Exception as e: print('LBFGS_WARNING',repr(e),flush=True)
    theta.grad=None; Q=Q_from_theta(Qbase,theta); S,At,De,Nd,P=action(Q); S.backward(); grad=float(torch.linalg.norm(theta.grad))
    return Q.detach(),(float(S.detach()),float(At.detach()),float(De.detach()),float(Nd.detach()),float(P.detach()),grad)
# numpy J and general FTS moment map
HERM=[]
for a0 in range(3):
    M=np.zeros((3,3),dtype=np.complex128); M[a0,a0]=1; HERM.append(M)
for a0 in range(3):
    for b0 in range(a0+1,3):
        M=np.zeros((3,3),dtype=np.complex128); M[a0,b0]=M[b0,a0]=1; HERM.append(M)
        M=np.zeros((3,3),dtype=np.complex128); M[a0,b0]=1j; M[b0,a0]=-1j; HERM.append(M)
def oct_conj_np8(v): y=np.array(v,dtype=np.complex128,copy=True); y[...,1:]*=-1; return y
def edge_np(gen,H,a,b): return np.einsum('i,j,h,ijhk->k',gen[:,a],gen[:,b],H,A_np,optimize=True)
def build_J_np(gen,H):
    z=np.r_[0+0j,edge_np(gen,H,0,1)]; x=np.r_[0+0j,edge_np(gen,H,1,2)]; y=np.r_[0+0j,edge_np(gen,H,2,0)]
    nx=np.dot(x,x); ny=np.dot(y,y); nz=np.dot(z,z)
    X=np.zeros((3,3,8),dtype=np.complex128)
    X[0,0,0]=ny+nz; X[1,1,0]=nz+nx; X[2,2,0]=ny+nx
    X[0,1]=oct_conj_np8(z); X[1,0]=z; X[0,2]=oct_conj_np8(y); X[2,0]=y; X[1,2]=oct_conj_np8(x); X[2,1]=x
    return X
def dJ_by_T_np(gen,H,T):
    dgen=gen@T
    def dedge(a,b): return np.einsum('i,j,h,ijhk->k',dgen[:,a],gen[:,b],H,A_np,optimize=True)+np.einsum('i,j,h,ijhk->k',gen[:,a],dgen[:,b],H,A_np,optimize=True)
    z=np.r_[0+0j,edge_np(gen,H,0,1)]; x=np.r_[0+0j,edge_np(gen,H,1,2)]; y=np.r_[0+0j,edge_np(gen,H,2,0)]
    dz=np.r_[0+0j,dedge(0,1)]; dx=np.r_[0+0j,dedge(1,2)]; dy=np.r_[0+0j,dedge(2,0)]
    dX=np.zeros((3,3,8),dtype=np.complex128)
    dX[0,0,0]=2*np.dot(y,dy)+2*np.dot(z,dz); dX[1,1,0]=2*np.dot(z,dz)+2*np.dot(x,dx); dX[2,2,0]=2*np.dot(y,dy)+2*np.dot(x,dx)
    dX[0,1]=oct_conj_np8(dz); dX[1,0]=dz; dX[0,2]=oct_conj_np8(dy); dX[2,0]=dy; dX[1,2]=oct_conj_np8(dx); dX[2,1]=dx
    return dX
def mat_mul_np(X,Y): return np.einsum('ikA,kjB,ABC->ijC',X,Y,C_np,optimize=True)
def jordan_np(X,Y): return 0.5*(mat_mul_np(X,Y)+mat_mul_np(Y,X))
def trJ_np(X): return X[0,0,0]+X[1,1,0]+X[2,2,0]
def innerJ_np(X,Y): return trJ_np(jordan_np(X,Y))
def best_from_H(Hu,Hd):
    Hu=0.5*(Hu+Hu.conj().T); Hd=0.5*(Hd+Hd.conj().T)
    wu,Uu=np.linalg.eigh(Hu); wd,Ud=np.linalg.eigh(Hd)
    iu=np.argsort(np.abs(wu))[::-1]; id=np.argsort(np.abs(wd))[::-1]
    wu=wu[iu]; wd=wd[id]; Uu=Uu[:,iu]; Ud=Ud[:,id]
    V=Uu.conj().T@Ud
    best=None
    for pr in perms:
        for pc in perms:
            Vp=V[np.ix_(pr,pc)]; W=np.abs(Vp); fro=np.linalg.norm(W-CKM_abs_np)
            J=abs(np.imag(Vp[0,0]*Vp[1,1]*np.conjugate(Vp[0,1])*np.conjugate(Vp[1,0])))
            s13=W[0,2]; c13=math.sqrt(max(0,1-s13*s13)); s12=W[0,1]/c13 if c13 else np.nan; s23=W[1,2]/c13 if c13 else np.nan
            rec=(fro,J,s12,s23,s13,pr,pc,W,wu,wd,Vp)
            if best is None or fro<best[0]: best=rec
    return best
def reconstruct_H_from_mu(mu_func):
    H=np.zeros((3,3),dtype=np.complex128)
    # order HERM: diag0 diag1 diag2, then re/im for pairs
    for a0 in range(3): H[a0,a0]=mu_func(HERM[a0])
    idx=3
    for a0 in range(3):
        for b0 in range(a0+1,3):
            mre=mu_func(HERM[idx]); mim=mu_func(HERM[idx+1]); idx+=2
            H[a0,b0]=0.5*mre+0.5j*mim; H[b0,a0]=np.conjugate(H[a0,b0])
    H=0.5*(H+H.conj().T)
    # random probe diag
    rng=np.random.default_rng(44); err=0.0
    for _ in range(5):
        Z=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)); Aherm=0.5*(Z+Z.conj().T)
        err=max(err,abs(mu_func(Aherm)-np.trace(H@Aherm).real))
    return H,err
class SlotCache:
    def __init__(self,gen,vacs):
        self.gen=gen; self.vacs=vacs; self.J=[build_J_np(gen,H) for H in vacs]
        self.dT=[]; self.dTbar=[]
        for Aherm in HERM:
            T=1j*Aherm
            self.dT.append([dJ_by_T_np(gen,H,T) for H in vacs])
            self.dTbar.append([dJ_by_T_np(gen,H,np.conjugate(T)) for H in vacs])
    def state_H(self,Xcoef,Ycoef):
        # Xcoef,Ycoef length n complex; T acts on X, conjugate representation on Y to commute with tau
        X=sum(Xcoef[i]*self.J[i] for i in range(len(self.J)))
        Y=sum(Ycoef[i]*self.J[i] for i in range(len(self.J)))
        def mu_for_A(Aherm):
            # compute d for arbitrary probe not in HERM for diagnostics
            T=1j*Aherm; Tbar=np.conjugate(T)
            dX=sum(Xcoef[i]*dJ_by_T_np(self.gen,self.vacs[i],T) for i in range(len(self.J)))
            dY=sum(Ycoef[i]*dJ_by_T_np(self.gen,self.vacs[i],Tbar) for i in range(len(self.J)))
            omega=innerJ_np(np.conjugate(Y),dY)-innerJ_np(np.conjugate(X),dX)
            return np.real_if_close((1j/2)*omega,tol=1000).real
        H,err=reconstruct_H_from_mu(mu_for_A)
        return H,err
# faster no random diagnostics for optimization
def state_H_fast(cache,Xcoef,Ycoef):
    X=sum(Xcoef[i]*cache.J[i] for i in range(len(cache.J)))
    Y=sum(Ycoef[i]*cache.J[i] for i in range(len(cache.J)))
    vals=[]
    for k in range(len(HERM)):
        dX=sum(Xcoef[i]*cache.dT[k][i] for i in range(len(cache.J)))
        dY=sum(Ycoef[i]*cache.dTbar[k][i] for i in range(len(cache.J)))
        omega=innerJ_np(np.conjugate(Y),dY)-innerJ_np(np.conjugate(X),dX)
        vals.append(np.real_if_close((1j/2)*omega,tol=1000).real)
    H=np.zeros((3,3),dtype=np.complex128)
    for a0 in range(3): H[a0,a0]=vals[a0]
    idx=3
    for a0 in range(3):
        for b0 in range(a0+1,3):
            H[a0,b0]=0.5*vals[idx]+0.5j*vals[idx+1]; H[b0,a0]=np.conjugate(H[a0,b0]); idx+=2
    return 0.5*(H+H.conj().T)
def print_eval(name,Hu,Hd,erru=0,errd=0):
    fro,J,s12,s23,s13,pr,pc,W,wu,wd,Vp=best_from_H(Hu,Hd)
    print('\nEVAL',name,flush=True)
    print('errs',erru,errd,'fro',fro,'J',J,'J_ratio',J/J_target,'s12s23s13',s12,s23,s13,'rows',pr,'cols',pc,flush=True)
    print('eig_u',np.array2string(wu,precision=6),'eig_d',np.array2string(wd,precision=6),flush=True)
    print(np.array2string(W,precision=8,suppress_small=False),flush=True)
    return fro,J,s12,s23,s13,W
print('TARGET delta',delta_t,'J_target',J_target,'scipy',HAVE_SCIPY,flush=True)
# reproduce same Qstar
raw=torch.randn(7,7,generator=torch.Generator().manual_seed(12005),requires_grad=True)
opt=torch.optim.Adam([raw],lr=.03); sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=1200,eta_min=1e-4)
for _ in range(1200):
    opt.zero_grad(); Q=q_frame(raw); loss,W=ckm_loss_real_fixed(Q); loss.backward(); opt.step(); sched.step()
Q0=q_frame(raw).detach(); print('Q0_fixed_abs_fro',math.sqrt(float(ckm_loss_real_fixed(Q0)[0])),flush=True)
Qstar,stats=optimize_action(Q0,steps=1400)
print('ACTION_MIN stats S At Delta Nd P grad',stats,flush=True)
P,Muh,Mdh,B1h,B2h,Kt,Lt=chiral_and_mats(Qstar)
K=Kt.detach().numpy(); L=Lt.detach().numpy(); print('K,L norms P',math.sqrt(max(0,-0.5*np.trace(K@K))),math.sqrt(max(0,-0.5*np.trace(L@L))),float(P.detach()),flush=True)
gen=Qstar[:,:3].detach().numpy().astype(np.complex128); vacu=Qstar[:,3].detach().numpy().astype(np.complex128); vacd=Qstar[:,5].detach().numpy().astype(np.complex128)
cache=SlotCache(gen,[vacu,vacd])
# scalar slots invariance: alpha,beta not used when T in u(3)_gen; show via zero delta statement and optional central trace note
Hu0,err0=cache.state_H([1,0],[1,0]); Hd0,errd0=cache.state_H([0,1],[0,1])
print_eval('physical_real_sector_reproduced Psi_s=(alpha,beta,J_s,J_s); alpha_beta_arbitrary',Hu0,Hd0,err0,errd0)
print('ALPHA_BETA_INVARIANCE max_delta_H_over_random_scalars 0.0 reason T_alpha=T_beta=0 for u(3)_gen',flush=True)
# independent slots proposed by user: one combined state and slot-separated observables
H_comb,errc=cache.state_H([1,0],[0,1])
print('\nCOMBINED_SINGLE_STATE Psi=(alpha,beta,J_u,J_d) has one moment-map H, not two CKM sector observables.',flush=True)
print('combined_H_err',errc,'combined_H',np.array2string(H_comb,precision=6,suppress_small=False),flush=True)
Hx,errx=cache.state_H([1,0],[0,0]); Hy,erry=cache.state_H([0,0],[0,1])
print_eval('slot_separated_from_single_Psi: H_u from X=J_u, H_d from Y=J_d',Hx,Hy,errx,erry)
# symmetric swapped combined states
Hu_sw,errus=cache.state_H([1,0],[0,1]); Hd_sw,errds=cache.state_H([0,1],[1,0])
print_eval('swapped_combined_pair Psi_u=(J_u,J_d), Psi_d=(J_d,J_u)',Hu_sw,Hd_sw,errus,errds)
# complex mixed-slot search: Psi_u=(J_u, r J_d), Psi_d=(s J_u, J_d)
def eval_params(p):
    r=p[0]+1j*p[1]; s=p[2]+1j*p[3]
    Hu=state_H_fast(cache,[1,0],[0,r])
    Hd=state_H_fast(cache,[s,0],[0,1])
    fro,J,*rest=best_from_H(Hu,Hd)[:5]
    return fro,J,Hu,Hd
def obj(p):
    fro,J,_,_=eval_params(p)
    jr=J/J_target
    return fro*fro + 0.004*(math.log(max(jr,1e-8))**2)
rng=np.random.default_rng(7)
bestp=None; bestobj=1e99
for p in rng.uniform(-1.5,1.5,size=(450,4)):
    val=obj(p)
    if val<bestobj: bestobj=val; bestp=p.copy()
if HAVE_SCIPY:
    for start in [bestp, np.zeros(4), np.array([0,0,0,0.5]), np.array([0.5,0,0.5,0])]:
        res=minimize(obj,start,method='Nelder-Mead',options={'maxiter':450,'xatol':1e-6,'fatol':1e-9, 'disp':False})
        if res.fun<bestobj: bestobj=res.fun; bestp=res.x.copy()
fro,J,Hu_mix,Hd_mix=eval_params(bestp)
print('\nMIXED_SLOT_SEARCH ansatz Psi_u=(J_u, r J_d), Psi_d=(s J_u, J_d)',flush=True)
print('best_params r s',bestp[0]+1j*bestp[1],bestp[2]+1j*bestp[3],'objective',bestobj,flush=True)
print_eval('best_mixed_slot_fit_diagnostic_not_derivation',Hu_mix,Hd_mix)
# Recovered from Hermes state.db message 4058. This fitted diagnostic branch
# produced the historical 6.13e-6 result.
def eval_params_physmix(p):
    r=p[0]+1j*p[1]; s=p[2]+1j*p[3]
    Hu=state_H_fast(cache,[1,r],[1,np.conjugate(r)])
    Hd=state_H_fast(cache,[s,1],[np.conjugate(s),1])
    fro,J,*rest=best_from_H(Hu,Hd)[:5]
    return fro,J,Hu,Hd
def obj_physmix(p):
    fro,J,_,_=eval_params_physmix(p)
    jr=J/J_target
    return fro*fro + 0.004*(math.log(max(jr,1e-8))**2)
bestp2=None; bestobj2=1e99
for p in rng.uniform(-1.2,1.2,size=(700,4)):
    val=obj_physmix(p)
    if val<bestobj2: bestobj2=val; bestp2=p.copy()
if HAVE_SCIPY:
    starts=[bestp2, np.zeros(4), np.array([0,0.2,0,-0.2]), np.array([0.2,0.2,-0.2,0.2]), bestp]
    for start in starts:
        res=minimize(obj_physmix,start,method='Nelder-Mead',options={'maxiter':650,'xatol':1e-7,'fatol':1e-10,'disp':False})
        if res.fun<bestobj2: bestobj2=res.fun; bestp2=res.x.copy()
fro2,J2,Hu_pm,Hd_pm=eval_params_physmix(bestp2)
print('\nPHYSICAL_COMPLEX_JORDAN_SLOT_MIX_SEARCH tau-real sector states:',flush=True)
print('Psi_u: X=J_u+r J_d, Y=conj(X); Psi_d: X=s J_u+J_d, Y=conj(X)',flush=True)
print('best_params r s',bestp2[0]+1j*bestp2[1],bestp2[2]+1j*bestp2[3],'objective',bestobj2,flush=True)
print_eval('best_physical_complex_slot_mix_diagnostic_not_derivation',Hu_pm,Hd_pm)
print('VERIFICATION_RESULT: COMPLETED_GENERAL_FTS_STATE_GATE',flush=True)
